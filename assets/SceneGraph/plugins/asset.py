#!/usr/bin/env python
from SceneGraph.core.nodes import DagNode


class AssetNode(DagNode):
    
    node_type     = 'asset'
    node_class    = 'container'
    node_category = 'builtin'
    default_name  = 'asset'
    default_color = [174, 188, 43, 255]

    def __init__(self, name=None, **kwargs):
        DagNode.__init__(self, name, **kwargs)
