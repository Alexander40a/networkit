#!/usr/bin/env python3
import unittest
import os
import networkit as nk


class TestGEXFIO(unittest.TestCase):

    def setUp(self):
        from networkit.graphio import GEXFReader

        self.reader = GEXFReader()
        # celegans.gexf from http://gexf.net/format/datasets.html
        self.g, self.events = self.reader.read("input/staticTest.gexf")
        # dynamics.gexf from http://gexf.net/format/datasets.html
        self.g2, self.events2 = self.reader.read("input/dynamicTest.gexf")
        # a random dynamic gexf file generated by gephi with dynamic weights
        self.g3, self.events3 = self.reader.read("input/dynamicTest2.gexf")
        # a simple dynamic weighted graph
        self.g4, self.events4 = self.reader.read("input/dynamicTest3.gexf")

    def checkStatic(self, graph, graph2):
        self.assertEqual(graph.isDirected(), graph2.isDirected())
        self.assertEqual(graph.isWeighted(), graph2.isWeighted())
        self.assertEqual(graph.numberOfNodes(), graph2.numberOfNodes())
        graph_edges = sorted([(u, v) for u, v in graph.iterEdges()])
        graph2_edges = sorted([(u, v) for u, v in graph2.iterEdges()])
        self.assertEqual(graph_edges, graph2_edges)

    def checkDynamic(self, eventStream, eventStream2):
        from networkit.dynamics import GraphEvent

        self.assertEqual(len(eventStream), len(eventStream2))
        # Check if timesteps are occuring at the same indexes
        index = 0
        for i in range(0, len(eventStream)):
            event = eventStream[i]
            event2 = eventStream2[i]
            if event.type == GraphEvent.TIME_STEP:
                self.assertEqual(GraphEvent.TIME_STEP, event2.type)
                old_index = index
                index = i
                # check if # of events between each timestep is equal
                self.assertEqual(
                    len(eventStream[old_index:index]),
                    len(eventStream2[old_index:index]),
                )

    def test_read_and_write(self):
        # write and read files again to check
        from networkit.graphio import GEXFWriter

        writer = GEXFWriter()
        writer.write(self.g, "output/staticTestResult.gexf", self.events)
        self.assertTrue(os.path.isfile("output/staticTestResult.gexf"))
        writer.write(self.g2, "output/dynamicTestResult.gexf", self.events2)
        self.assertTrue(os.path.isfile("output/dynamicTestResult.gexf"))
        writer.write(self.g3, "output/dynamicTest2Result.gexf", self.events3)
        self.assertTrue(os.path.isfile("output/dynamicTest2Result.gexf"))
        writer.write(self.g4, "output/dynamicTest3Result.gexf", self.events4)
        self.assertTrue(os.path.isfile("output/dynamicTest3Result.gexf"))

        gTest, testEvents = self.reader.read("output/staticTestResult.gexf")
        g2Test, testEvents2 = self.reader.read("output/dynamicTestResult.gexf")
        g3Test, testEvents3 = self.reader.read("output/dynamicTest2Result.gexf")
        g4Test, testEvents4 = self.reader.read("output/dynamicTest3Result.gexf")

        # 1. check properties and static elements
        self.checkStatic(self.g, gTest)
        self.checkStatic(self.g2, g2Test)
        self.checkStatic(self.g3, g3Test)
        self.checkStatic(self.g4, g4Test)
        # 2.check events
        self.checkDynamic(self.events, testEvents)
        self.checkDynamic(self.events2, testEvents2)
        self.checkDynamic(self.events3, testEvents3)
        self.checkDynamic(self.events4, testEvents4)


class TestMTXGraphReader(unittest.TestCase):
    def testRead(self):
        reader = nk.graphio.MTXGraphReader()
        graph = reader.read("input/chesapeake.mtx")
        self.assertEqual(graph.numberOfNodes(), 39)
        self.assertEqual(graph.numberOfEdges(), 170)
        self.assertFalse(graph.isDirected())
        self.assertTrue(graph.hasEdge(3, 16))
        self.assertTrue(graph.hasEdge(16, 3))


class TestRBGraphReader(unittest.TestCase):
    def testRead(self):
        reader = nk.graphio.RBGraphReader()
        graph = reader.read("input/tiny_05.rb")
        self.assertEqual(graph.numberOfNodes(), 5)
        self.assertEqual(graph.numberOfEdges(), 11)
        self.assertTrue(graph.isDirected())
        self.assertTrue(graph.hasEdge(0, 0))
        self.assertEqual(graph.weight(1, 4), 10)


class TestGraphIO(unittest.TestCase):

    def checkStatic(self, graph, graph2):
        self.assertEqual(graph.isDirected(), graph2.isDirected())
        self.assertEqual(graph.isWeighted(), graph2.isWeighted())
        self.assertEqual(graph.numberOfNodes(), graph2.numberOfNodes())
        graph_edges = sorted([(u, v) for u, v in graph.iterEdges()])
        graph2_edges = sorted([(u, v) for u, v in graph2.iterEdges()])
        self.assertEqual(graph_edges, graph2_edges)

    def testWriteGraphReadGraph(self):
        G = nk.generators.ErdosRenyiGenerator(100, 0.1).generate()

        # we do not have writer and reader classes for these formats:
        excluded_formats = set(
            [
                nk.Format.KONECT,
                nk.Format.DOT,
                nk.Format.GraphViz,
                nk.Format.SNAP,
                nk.Format.MatrixMarket,
                nk.Format.RB,
            ]
        )

        for format in nk.Format:
            if format in excluded_formats:
                # format do not support both reading and writing
                continue

            filename = "output/testWriteGraphReadGraph." + str(format)
            if format == nk.Format.MAT:
                filename += ".mat"  # suffix required

            if os.path.exists(filename):
                os.remove(filename)

            kargs = [" ", 0] if format == nk.Format.EdgeList else []
            nk.graphio.writeGraph(G, filename, format, *kargs)
            if format == nk.Format.GEXF:
                G1, _ = nk.graphio.readGraph(filename, format, *kargs)
            else:
                G1 = nk.graphio.readGraph(filename, format, *kargs)
            self.checkStatic(G, G1)

    def testGuessFormat(self):
        instances = [
            ("airfoil1.graph", nk.Format.METIS),
            ("comments.edgelist", nk.Format.EdgeListTabOne),
            ("dynamicTest.gexf", nk.Format.GEXF),
            ("foodweb-baydry.konect", nk.Format.KONECT),
            ("foodweb-baydry.nkbg002", nk.Format.NetworkitBinary),
            ("foodweb-baydry.nkbg003", nk.Format.NetworkitBinary),
            ("jazz2_directed.gml", nk.Format.GML),
            ("chesapeake.mtx", nk.Format.MatrixMarket),
            ("tiny_05.rb", nk.Format.RB),
        ]

        for file, expected_result in instances:
            guess = nk.graphio.guessFileFormat(f"input/{file}")
            self.assertEqual(guess, expected_result)

    def testGuessFormatInputGraphs(self):
        # this test does not check the guess result;
        # it is just used to make sure (most) graphs in our input directory are readable by the guess format code
        excludeFiles = [
            "README.md",
            "celegans_metabolic.thrill",
            "community.dat",
            "community_overlapping.dat",
            "community_overlapping.cover",
            "example2.dgs",
            "example_write.dgs",
            "airfoil1-10p.png",
            "alphabet.edgelist",
            "testLFR",
            "airfoil1.gi",
            "spaceseparated_weighted.edgelist",
        ]
        for file in os.listdir("input"):
            if file not in excludeFiles:
                with self.subTest(file=file):
                    nk.graphio.guessFileFormat(f"input/{file}")

    def testBinaryFormatVersionUpgrade(self):
        output_filepath = "output/testBinaryFormatVersionUpgrade.nkbg"
        nk.graphio.writeGraph(
            nk.graphio.readGraph("input/foodweb-baydry.nkbg002"),
            output_filepath,
            nk.Format.NetworkitBinary,
        )
        with open(output_filepath, "rb") as f:
            nkmagicbits = f.read(7)
            self.assertEqual(
                nkmagicbits, bytes([0x6E, 0x6B, 0x62, 0x67, 0x30, 0x30, 0x33])
            )


if __name__ == "__main__":
    unittest.main()
