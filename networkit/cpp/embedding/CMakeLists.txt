networkit_add_module(embedding
    AliasSampler.cpp
    BiasedRandomWalk.cpp
    LearnEmbedding.cpp
    Node2Vec.cpp
    KHop.cpp
    )

networkit_module_link_modules(embedding
        auxiliary graph linkprediction)

add_subdirectory(test)

