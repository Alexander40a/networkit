//
// Created by andreas on 03.01.25.
//

#ifndef NETWORKIT_PLANARITY_LEFT_RIGHT_PLANARITY_TEST_HPP_
#define NETWORKIT_PLANARITY_LEFT_RIGHT_PLANARITY_TEST_HPP_
#include <networkit/base/Algorithm.hpp>
#include <networkit/graph/Graph.hpp>

namespace NetworKit {

class LeftRightPlanarityTest final : public Algorithm {

public:
    LeftRightPlanarityTest(const Graph &graph) : graph_(&graph) {
        dfsGraph = Graph(graph_->numberOfNodes(), false, true, false);
    }
    void run() override;
    bool isPlanar() const { return isPlanar_; }

private:
    static constexpr Edge noneEdge{};
    static constexpr count noneHeight{std::numeric_limits<count>::max()};

    struct Interval {
        Edge low{noneEdge};
        Edge high{noneEdge};

        Interval() : low{noneEdge}, high{noneEdge} {};
        Interval(const Edge &low, const Edge &high) : low(low), high(high) {}
        bool isEmpty() const { return low == noneEdge && high == noneEdge; }

        friend bool operator==(const Interval &lhs, const Interval &rhs) {
            return lhs.low == rhs.low && lhs.high == rhs.high;
        }
    };

    struct ConflictPair {
        Interval left{};
        Interval right{};

        ConflictPair() = default;
        ConflictPair(const Interval &left, const Interval &right) : left(left), right(right) {}

        void swap() { std::swap(left, right); }

        friend bool operator==(const ConflictPair &lhs, const ConflictPair &rhs) {
            return lhs.left == rhs.left && lhs.right == rhs.right;
        }
    };
    const ConflictPair NoneConflictPair{Interval(), Interval()};

    const Graph *graph_;
    bool isPlanar_{};
    void dfsOrientation(node startNode);
    bool dfsTesting(node startNode);
    bool applyConstraints(Edge edge, Edge parentEdge);
    void removeBackEdges(Edge edge);
    void sortAdjacencyListByNestingDepth();
    bool conflicting(const Interval &interval, const Edge &edge);
    count getLowestLowPoint(const ConflictPair &conflictPair);
    std::vector<count> heights;
    std::unordered_map<Edge, count> lowestPoint;
    std::unordered_map<Edge, count> secondLowestPoint;
    std::unordered_map<Edge, Edge> ref;
    std::vector<node> roots;
    std::unordered_map<Edge, Edge> lowestPointEdge;
    std::unordered_map<Edge, count> nestingDepth;
    std::unordered_map<index, Edge> parentEdges;
    std::stack<ConflictPair> stack;
    std::unordered_map<Edge, ConflictPair> stackBottom;
    Graph dfsGraph;
};
} // namespace NetworKit
#endif // NETWORKIT_PLANARITY_LEFT_RIGHT_PLANARITY_TEST_HPP_
