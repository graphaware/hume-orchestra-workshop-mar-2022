import json

from munch import *
import yaml


class Entry:
    apiVersion = "v1"
    kind = None
    metadata = None
    spec = None

    def toYaml(self):
        return Munch(
            apiVersion=self.apiVersion,
            kind=self.kind,
            metadata=self.metadata,
            spec=self.spec).toYAML()

    def toYamlFile(self, fileName):
        open(fileName, "w").write(self.toYaml())

    @staticmethod
    def fromYamlFile(fileName):
        data = munchify(yaml.safe_load(open(fileName)))
        ret = Entry()
        ret.apiVersion = data.apiVersion
        ret.kind = data.kind
        ret.metadata = data.metadata
        ret.spec = data.spec
        return ret


class Workflow(Entry):
    kind = "Workflow"

    def __init__(self, name, label):
        self.metadata = Munch(name=name)
        self.spec = Munch(label=label, components=[])

    @classmethod
    def fromJsonExport(cls, fileName):
        data = munchify(json.load(open(fileName)))
        workflow = cls(data.name.replace(" ", "-"), data.name)
        for inComponent in data.components:
            component = Component(inComponent.name, inComponent.type, **inComponent.config)
            if inComponent.resource is not None:
                component.setResource(inComponent.resource)
            component.data.to = inComponent.to
            workflow.addComponent(component)
        return workflow

    def addComponent(self, component):
        self.spec.components.append(component.data)


class Component:
    def __init__(self, name, type, **config):
        self.data = Munch(
            name=name,
            type=type,
            config=Munch(config),
            to=[])

    def setResource(self, name):
        self.data.resource = Munch(selector=Munch(name=name))

    def connect(self, to):
        self.data.to.append(to.data.name)
        return self


Types = Munch(
    neo4jReader="#Hume.Orchestra.DataSource.Neo4jReader",
    timer="#Hume.Orchestra.Clock.Timer",
    jdbcReader="#Hume.Orchestra.DataSource.JDBC",
    observer="#Hume.Orchestra.Monitor.Observer",
    messageTransformer="#Hume.Orchestra.Processor.MessageTransformer",
    cypherQuery="#Hume.Orchestra.Processor.Cypher",
    neo4jWriter="#Hume.Orchestra.Persistence.Neo4jWriter",
    batchProcessor="#Hume.Orchestra.Processor.Batch", )


def generatePipeline(w, name):
    once = Component(f"Once{name}", Types.timer, period=10000, delay=1)
    w.addComponent(once)

    table = Component(f"{name}Table", Types.jdbcReader, query=f'SELECT * FROM "{name}"')
    table.setResource("Local-SQL")
    w.addComponent(table)
    once.connect(to=table)

    readObserver = Component(f"{name} Read Observer", Types.observer)
    w.addComponent(readObserver)
    table.connect(to=readObserver)

    wrapTable = Component(f"Wrap{name}", Types.messageTransformer, transformer_script=f"""
        return {{
          "id": body["{name}Id"],
          "item" : body
        }}
        """)
    w.addComponent(wrapTable)
    table.connect(to=wrapTable)

    batchTable = Component(f"Batch{name}", Types.batchProcessor, batch_size=1000, batch_timeout=300)
    w.addComponent(batchTable)
    wrapTable.connect(to=batchTable)

    cypherQuery = Component(f"Cypher {name} Query", Types.cypherQuery, query=f"""
        UNWIND $_batch as record
        MERGE (c:{name} {{{name}Id:record.id}})
        ON CREATE 
          SET c = record.item""")
    w.addComponent(cypherQuery)
    batchTable.connect(to=cypherQuery)

    cypherWriter = Component(f"{name} Write", Types.neo4jWriter, stream_records=False)
    cypherWriter.setResource("Local-Neo4j")
    w.addComponent(cypherWriter)
    cypherQuery.connect(to=cypherWriter)

    writeObserver = Component(f"{name} Write Observer", Types.observer)
    w.addComponent(writeObserver)
    cypherWriter.connect(to=writeObserver)


def main():
    # create a new empty workflow
    w = Workflow("generated-workflow", "Generated Workflow")

    # use generation function to create two ingestion pipelines
    generatePipeline(w, "Playlist")
    generatePipeline(w, "Track")

    # store the file into configuration folder
    w.toYamlFile("../config/hume/workflow-knowledge-graph/init-generated-workflow.yml")

    # update the knowledge graph configuration to include the newly created workflow
    kgFile = "../config/hume/workflow-knowledge-graph/init-knowledge-graph.yml"
    kg = Entry.fromYamlFile(kgFile)
    if w.metadata.name not in kg.spec.workflows:
        kg.spec.workflows.append(w.metadata.name)
        kg.toYamlFile(kgFile)


if __name__ == '__main__':
    main()
