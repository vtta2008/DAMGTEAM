#!/usr/bin/env python
import sys
from PySide import QtCore, QtGui
from SceneGraph.core import log
from SceneGraph import options

"""
pyqtgraph:

    - Node = QObject
        Node.graphicsItem = QGraphicsObject

    def close(self):
        self.disconnectAll()
        self.clearTerminals()
        item = self.graphicsItem()
        if item.scene() is not None:
            item.scene().removeItem(item)
        self._graphicsItem = None
        w = self.ctrlWidget()
        if w is not None:
            w.setParent(None)
        #self.emit(QtCore.SIGNAL('closed'), self)
        self.sigClosed.emit(self)

My Node:
    Requirements:
        - needs to send signals from label
        - needs to have connections

Node.setHandlesChildEvents(False)

"""

class Node(QtGui.QGraphicsObject):

    Type = QtGui.QGraphicsObject.UserType + 1
    doubleClicked     = QtCore.Signal()
    nodeChanged       = QtCore.Signal(object)  

    def __init__(self, dagnode, parent=None):
        super(Node, self).__init__(parent)

        self.dagnode         = dagnode
        self.dagnode._widget = self
        
        # attributes
        self.bufferX         = 3
        self.bufferY         = 3
        self.pen_width       = 1.5                    # pen width for NodeBackground  

        # widget colors
        self._l_color        = [5, 5, 5, 255]         # label color
        self._p_color        = [10, 10, 10, 255]      # pen color (outer rim)
        self._s_color        = [0, 0, 0, 60]          # shadow color

        # widget globals
        self._debug          = False
        self.is_selected     = False                  # indicates that the node is selected
        self.is_hover        = False                  # indicates that the node is under the cursor
        self._render_effects = True                   # enable fx
        self._label_coord    = [0,0]                  # default coordiates of label

        # connections widget
        self.connections     = dict(input  = dict(),
                                    output = dict(),
                                    )

        self.setHandlesChildEvents(False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)

        self.setFlag(QtGui.QGraphicsObject.ItemSendsGeometryChanges, True)
        self.setFlag(QtGui.QGraphicsObject.ItemSendsScenePositionChanges, True)
        self.setAcceptsHoverEvents(True)

        # layers
        self.background = NodeBackground(self)
        self.label = NodeLabel(self)   

        # signals/slots
        self.label.doubleClicked.connect(self.labelDoubleClickedEvent)

        # set node position
        self.setPos(QtCore.QPointF(self.dagnode.pos[0], self.dagnode.pos[1]))

        # build the connection widgets.
        self.buildConnections()

    #- Attributes ----
    @property
    def width(self):
        return float(self.dagnode.width)
        
    @width.setter
    def width(self, val):
        self.dagnode.width = val

    @property
    def height(self):
        return float(self.dagnode.height)

    @height.setter
    def height(self, val):
        self.dagnode.height = val

    @property
    def color(self):
        """
        Return the 'node color' (background color)
        """
        return self.dagnode.color

    @color.setter
    def color(self, val):
        """
        Return the 'node color' (background color)
        """
        self.dagnode.color = val

    @property
    def orientation(self):
        return self.dagnode.orientation

    @orientation.setter
    def orientation(self, val):
        self.dagnode.orientation = val
        return self.dagnode.orientation

    @property
    def is_enabled(self):
        return self.dagnode.enabled

    @is_enabled.setter
    def is_enabled(self, val):
        self.dagnode.enabled = val
        return self.dagnode.enabled

    @property
    def is_expanded(self):
        return self.dagnode.expanded

    @is_expanded.setter
    def is_expanded(self, val):
        self.dagnode.expanded = val
        return self.dagnode.expanded

    #- TESTING ---
    def labelDoubleClickedEvent(self):
        """
        Signal when the label item is double-clicked.

         * currently not using
        """
        val = self.label.is_editable
        #self.label.setTextEditable(not val)

    #- Events ----
    def itemChange(self, change, value):
        """
        Default node 'changed' signal.

        ItemMatrixChange

        change == "GraphicsItemChange"
        """
        #print 'change: ', change.__class__.__name__
        if change == self.ItemPositionHasChanged:
            self.nodeChanged.emit(self)
        return super(Node, self).itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """
        translate Y: height_expanded - height_collapsed/2
        """
        expanded = self.dagnode.expanded
        self.dagnode.expanded = not self.dagnode.expanded
        self.update()

        # translate the node in relation to it's expanded height
        diffy = (self.dagnode.height_expanded - self.dagnode.base_height)/2
        if expanded:
            diffy = -diffy
        self.translate(0, diffy)
        self.nodeChanged.emit(self)
        QtGui.QGraphicsItem.mouseDoubleClickEvent(self, event)

    def boundingRect(self):
        w = self.width
        h = self.height
        bx = self.bufferX
        by = self.bufferY
        return QtCore.QRectF(-w/2 -bx, -h/2 - by, w + bx*2, h + by*2)

    @property
    def label_rect(self):
        return self.label.boundingRect()

    def shape(self):
        """
        Create the shape for collisions.
        """
        w = self.width + 4
        h = self.height + 4
        bx = self.bufferX
        by = self.bufferY
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(-w/2, -h/2, w, h), 7, 7)
        return path

    #- Global Properties ----
    @property
    def label_pos(self):
        return QtCore.QPointF(-self.width/2, -self.height/2 - self.bufferY)

    @property
    def input_pos(self):
        """
        Return the first input connection center point.

        returns:
            (QPointF) - input connection position.
        """
        rect = self.boundingRect()
        width = rect.width()
        height = rect.height()
        ypos = -rect.center().y()
        if self.is_expanded:         
            ypos = -(height / 2 ) +  self.dagnode.base_height * 2
        return QtCore.QPointF(-width/2, ypos)

    @property
    def output_pos(self):
        """
        Return the first output connection center point.

        returns:
            (QPointF) - output connection position.
        """
        rect = self.boundingRect()
        width = rect.width()
        height = rect.height()
        ypos = -rect.center().y()
        if self.is_expanded:         
            ypos = -(height / 2 ) +  self.dagnode.base_height * 2
        return QtCore.QPointF(width/2, ypos)

    @property
    def bg_color(self):
        """
        Returns the widget background color.

        returns:
            (QColor) - widget background color.
        """
        if not self.is_enabled:
            return QtGui.QColor(*[125, 125, 125])

        if self.is_selected:
            return QtGui.QColor(*[255, 183, 44])

        if self.is_hover:
            base_color = QtGui.QColor(*self.color)
            return base_color.lighter(125)
        return QtGui.QColor(*self.color)

    @property
    def pen_color(self):
        """
        Returns the widget pen color.

        returns:
            (QColor) - widget pen color.
        """
        if not self.is_enabled:
            return QtGui.QColor(*[40, 40, 40])
        if self.is_selected:
            return QtGui.QColor(*[251, 210, 91])
        return QtGui.QColor(*self._p_color)

    @property
    def label_color(self):
        """
        Returns the widget label color.

        returns:
            (QColor) - widget label color.
        """
        if not self.is_enabled:
            return QtGui.QColor(*[50, 50, 50])
        if self.is_selected:
            return QtGui.QColor(*[88, 0, 0])
        return QtGui.QColor(*self._l_color)

    @property
    def shadow_color(self):
        """
        Returns the node shadow color, as dictated
        by the dagnode.

        returns:
            (QColor) - shadow color.
        """
        if not self.is_enabled:
            return QtGui.QColor(*[35, 35, 35, 60])
        if self.is_selected:
            return QtGui.QColor(*[104, 56, 0, 60])
        return QtGui.QColor(*self._s_color)

    #- Connections -----
    @property
    def inputs(self):
        """
        Returns a list of dagnode input connections.

        returns:
            (list) - list of input connections.
        """
        return self.dagnode.inputs

    @property
    def outputs(self):
        """
        Returns a list of dagnode output connections.

        returns:
            (list) - list of output connections.
        """
        return self.dagnode.outputs

    def inputConnections(self):
        """
        Returns a list of input connection widgets.

        returns:
            (list) - list of input connection widgets.
        """
        return self.connections.get('input').values()

    def outputConnections(self):
        """
        Returns a list of output connection widgets.

        returns:
            (list) - list of output connection widgets.
        """
        return self.connections.get('output').values()

    def getConnection(self, name):
        """
        Returns a named connection.

        returns:
            (Connection) - connection widget.
        """
        if name not in self.inputs and name not in self.outputs:
            return 

        if name in self.inputs:
            return self.connections.get('input').get(name)

        if name in self.outputs:
            return self.connections.get('output').get(name)

    def buildConnections(self):
        """
        Build the nodes' connection widgets.
        """
        for input_name in self.dagnode.inputs:            
            # connection dag node
            input_dag = self.dagnode._inputs.get(input_name)
            input_widget = Connection(self, input_dag, input_name, **input_dag)
            self.connections['input'][input_name] = input_widget

        for output_name in self.dagnode.outputs:
            # connection dag node
            output_dag = self.dagnode._outputs.get(output_name)
            output_widget = Connection(self, output_dag, output_name, **output_dag)
            self.connections['output'][output_name] = output_widget

    def removeConnectionWidgets(self):
        """
        Remove all of the connection widgets.
        """
        for input_name in self.connections.get('input'):            
            input_widget = self.connections.get('input').get(input_name)
            self.scene().removeItem(input_widget)

        for output_name in self.dagnode.outputs:
            output_widget = self.connections.get('output').get(output_name)
            self.scene().removeItem(output_widget)

    def updateConnections(self):
        """
        Update all of the connection widgets.
        """
        i = 0
        for input_name in self.connections.get('input'):            
            input_widget = self.connections.get('input').get(input_name)
            input_pos = self.input_pos
            y_offset1 = 0
            if i:
                y_offset1 = self.dagnode.base_height * i
            input_pos.setY(input_pos.y() + y_offset1)
            input_widget.setPos(input_pos)
            i += 1

        o = 0
        for output_name in self.dagnode.outputs:
            output_widget = self.connections.get('output').get(output_name)
            output_pos = self.output_pos
            y_offset2 = 0
            if o:
                y_offset2 = self.dagnode.base_height * o
            output_pos.setY(output_pos.y() + y_offset2)
            output_widget.setPos(output_pos)
            o += 1

    def paint(self, painter, option, widget):
        """
        Paint the widget container and all of the child widgets.
        """
        self.is_selected = False
        self.is_hover = False

        if option.state & QtGui.QStyle.State_Selected:
            self.is_selected = True

        if option.state & QtGui.QStyle.State_MouseOver:
            self.is_hover = True

        # translate the label
        self.label.setPos(self.label_pos)
        self.updateConnections()

        if self._render_effects:
            # background
            self.bgshd = QtGui.QGraphicsDropShadowEffect()
            self.bgshd.setBlurRadius(16)
            self.bgshd.setColor(self.shadow_color)
            self.bgshd.setOffset(8,8)
            self.background.setGraphicsEffect(self.bgshd)

            # label
            self.lblshd = QtGui.QGraphicsDropShadowEffect()
            self.lblshd.setBlurRadius(8)
            self.lblshd.setColor(self.shadow_color)
            self.lblshd.setOffset(4,4)
            self.label.setGraphicsEffect(self.lblshd)

        if self._debug:
            debug_color = QtGui.QColor(*[0, 0, 0])
            painter.setBrush(QtCore.Qt.NoBrush)

            green_color = QtGui.QColor(0, 255, 0)
            painter.setPen(QtGui.QPen(green_color, 0.5, QtCore.Qt.SolidLine))
            painter.drawEllipse(self.output_pos, 4, 4)

            yellow_color = QtGui.QColor(255, 255, 0)
            painter.setPen(QtGui.QPen(yellow_color, 0.5, QtCore.Qt.SolidLine))   
            painter.drawEllipse(self.input_pos, 4, 4)


    def setDebug(self, val):
        """
        Set the debug value of all child nodes.
        """
        vs = 'true'
        if not val:
            vs = 'false'
        if val != self._debug:
            log.info('setting "%s" debug: %s' % (self.dagnode.name, vs))
            self._debug = val
            for item in self.childItems():
                if hasattr(item, '_debug'):
                    item._debug = val



class NodeLabel(QtGui.QGraphicsObject):
    
    doubleClicked     = QtCore.Signal()
    labelChanged      = QtCore.Signal()
    clicked           = QtCore.Signal()

    def __init__(self, parent):
        QtGui.QGraphicsObject.__init__(self, parent)
        
        self.dagnode        = parent.dagnode

        self._debug         = False
        self._font          = 'Monospace'
        self._font_size     = 8
        self._font_bold     = False
        self._font_italic   = False

        self.label = QtGui.QGraphicsTextItem(self.dagnode.name, self)
        self._document = self.label.document()

        self._document.setMaximumBlockCount(1)
        self._document.contentsChanged.connect(self.nodeNameChanged)

        # bounding shape
        self.rect_item = QtGui.QGraphicsRectItem(self.boundingRect(), self)
        self.rect_item.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        #self.rect_item.setPen(QtGui.QPen(QtGui.QColor(125,125,125)))        
        self.rect_item.pen().setStyle(QtCore.Qt.DashLine)
        self.rect_item.stackBefore(self.label)
        self.setHandlesChildEvents(False)

    @QtCore.Slot()
    def nodeNameChanged(self):
        """
        Runs when the node name is changed.
        """      
        new_name = self.text
        if new_name != self.dagnode.name:
            self.dagnode.name = new_name
            
        # re-center the label
        bounds = self.boundingRect()
        self.label.setPos(bounds.width()/2. - self.label.boundingRect().width()/2, 0)

    @property
    def is_editable(self):
        return self.label.textInteractionFlags() == QtCore.Qt.TextEditorInteraction

    def keyPressEvent(self, event):
        print '# NodeLabel: keyPressEvent'
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.nodeNameChanged()
        else:
            QtGui.QGraphicsObject.keyPressEvent(self, event)

    @property
    def node(self):
        return self.parentItem()

    def boundingRect(self):
        return self.label.boundingRect()

    @property
    def text(self):
        return str(self._document.toPlainText())

    @text.setter
    def text(self, text):
        self._document.setPlainText(text)
        return self.text

    def shape(self):
        """
        Aids in selection.
        """
        path = QtGui.QPainterPath()
        polyon = QtGui.QPolygonF(self.boundingRect())
        path.addPolygon(polyon)
        return path

    def paint(self, painter, option, widget):
        """
        Draw the label.
        """
        label_color = self.node.label_color
        label_italic = self._font_italic

        # diabled fonts always render italicized
        if not self.node.is_enabled:
            label_italic = True

        #painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        qfont = QtGui.QFont(self._font)
        qfont.setPointSize(self._font_size)
        qfont.setBold(self._font_bold)
        qfont.setItalic(label_italic)
        self.label.setFont(qfont)

        self.label.setDefaultTextColor(label_color)
        self.text = self.node.dagnode.name

        # debug
        if self._debug:
            qpen = QtGui.QPen(QtGui.QColor(125,125,125))
            qpen.setWidthF(0.5)
            qpen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(qpen)
            painter.drawPolygon(self.boundingRect())


class NodeBackground(QtGui.QGraphicsItem):
    def __init__(self, parent=None, scene=None):
        super(NodeBackground, self).__init__(parent, scene)

        self.dagnode = parent.dagnode
        self._debug  = False

    @property
    def node(self):
        return self.parentItem()

    @property 
    def pen_width(self):
        return self.node.pen_width

    def boundingRect(self):
        return self.node.boundingRect()

    def labelLine(self, offset=0):
        """
        Draw a line for the node label area
        """
        p1 = self.boundingRect().topLeft()
        p1.setX(p1.x() + self.node.bufferX)
        p1.setY(p1.y() + self.node.bufferY*7)

        p2 = self.boundingRect().topRight()
        p2.setX(p2.x() - self.node.bufferX)
        p2.setY(p2.y() + self.node.bufferY*7)

        if offset:
            p1.setY(p1.y() + offset)
            p2.setY(p2.y() + offset)

        return QtCore.QLineF(p1, p2)

    def paint(self, painter, option, widget):
        """
        Paint the node background.
        """
        # setup colors
        bg_clr1 = self.node.bg_color
        bg_clr2 = bg_clr1.darker(150)

        # background gradient
        gradient = QtGui.QLinearGradient(0, -self.node.height/2, 0, self.node.height/2)
        gradient.setColorAt(0, bg_clr1)
        gradient.setColorAt(1, bg_clr2)

        # pen color
        pcolor = self.node.pen_color
        qpen = QtGui.QPen(pcolor)
        qpen.setWidthF(self.pen_width)

        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(qpen)
        painter.drawRoundedRect(self.boundingRect(), 7, 7)

        # line pen #1
        lcolor = self.node.pen_color
        lcolor.setAlpha(80)
        lpen = QtGui.QPen(lcolor)
        lpen.setWidthF(0.5)

        if self.dagnode.expanded:
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(lpen)

            label_line = self.labelLine()
            painter.drawLine(label_line)



class Edge(QtGui.QGraphicsObject):
    
    Type        = QtGui.QGraphicsObject.UserType + 2
    adjustment  = 5

    def __init__(self, dagnode, *args, **kwargs):
        QtGui.QGraphicsObject.__init__(self, *args, **kwargs)

        self.dagnode         = dagnode

        # globals
        self._l_color        = [224, 224, 224]        # line color
        self._p_color        = [10, 10, 10, 255]      # pen color (outer rim)
        self._h_color        = [90, 245, 60]          # highlight color
        self._s_color        = [0, 0, 0, 60]          # shadow color
        
        self.visible         = True
        self._debug          = False
        self.is_enabled      = True                   # node is enabled (will eval)  
        self.is_selected     = False                  # indicates that the node is selected
        self.is_hover        = False                  # indicates that the node is under the cursor
        self._render_effects = True                   # enable fx

        self.arrow_size      = 8 
        self.show_conn       = False                  # show connection string
        self.multi_conn      = False                  # multiple connections (future)
        self.edge_type       = 'bezier'

        # connections
        self.source_item     = None
        self.dest_item       = None

        # points
        self.source_point    = QtCore.QPointF(0,0)
        self.dest_point      = QtCore.QPointF(0,0)
        self.center_point    = QtCore.QPointF(0,0)      
        
        # geometry
        self.bezier_path     = QtGui.QPainterPath()
        self.poly_line       = QtGui.QPolygonF()

        # flags
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)

        self.setFlag(QtGui.QGraphicsObject.ItemSendsGeometryChanges, True)
        self.setFlag(QtGui.QGraphicsObject.ItemSendsScenePositionChanges, True)
        self.setAcceptsHoverEvents(True)

    def setDebug(self, val):
        """
        Set the widget debug modeself.
        """
        if val != self._debug:
            self._debug = val

    def listConnections(self):
        """
        Returns a list of connected nodes.
        """
        return (self.source_item.node, self.dest_item.node)

    @property
    def source_node(self):
        """
        Returns the source node widget.
        """
        return self.source_item.node

    @property
    def dest_node(self):
        """
        Returns the destination node widget.
        """
        return self.dest_item.node

    @property
    def line_color(self):
        """
        Returns the current line color.
        """
        if self.is_selected:
            return QtGui.QColor(*self._h_color)
        if self.is_hover:
            base_color = QtGui.QColor(*self._l_color)
            return base_color.lighter(125)
        return QtGui.QColor(*self._l_color)



class Connection(QtGui.QGraphicsObject):
    
    Type                = QtGui.QGraphicsObject.UserType + 4
    clickedSignal       = QtCore.Signal(QtCore.QObject)
    nodeChanged         = QtCore.Signal(object)
    PRIVATE             = []

    def __init__(self, parent, conn_node, name, **kwargs):
        QtGui.QGraphicsObject.__init__(self, parent)

        self.dagnode        = parent.dagnode
        self.dagconn        = conn_node

        self.name           = name
        self.connections    = dict()
        self.draw_radius    = 4.0
        self.radius         = self.draw_radius*4
        self.buffer         = 2.0
        self.node_shape     = 'circle'
        
        self.draw_label     = False                  # draw a connection name label
        self.is_proxy       = False                  # connection is a proxy for several connections

        # widget colors
        self._l_color       = [5, 5, 5, 255]         # label color
        self._s_color       = [0, 0, 0, 60]          # shadow color
        self._p_color       = [178, 187, 28, 255]    # proxy node color

        # connection state
        self._debug         = False
        self.is_selected    = False
        self.is_hover       = False

        self.setAcceptHoverEvents(True)
        self.setFlags(QtGui.QGraphicsObject.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsFocusable)

    def __repr__(self):
        return 'Connection("%s.%s")' % (self.dagnode.name, self.name)

    @property
    def node(self):
        return self.parentItem()

    @property
    def is_input(self):
        return self.dagconn.is_input

    @is_input.setter
    def is_input(self, val):
        self.dagnode.is_input = val
        return self.dagconn.is_input

    @property
    def is_connected(self):
        return len(self.connections)  

    @property
    def orientation(self):
        return self.dagnode.orientation

    @orientation.setter
    def orientation(self, val):
        self.dagnode.orientation = val
        return self.dagnode.orientation

    @property
    def is_enabled(self):
        return self.dagnode.enabled

    @is_enabled.setter
    def is_enabled(self, val):
        self.dagnode.enabled = val
        return self.dagnode.enabled

    @property
    def is_expanded(self):
        return self.dagnode.expanded

    @is_expanded.setter
    def is_expanded(self, val):
        self.dagnode.expanded = val
        return self.dagnode.expanded

    @property
    def max_connections(self):
        return self.dagconn.max_connections

    @max_connections.setter
    def max_connections(self, val):
        self.dagconn.max_connections = val
        return self.max_connections

    @property
    def is_connectable(self):
        """
        Returns true if the connection can take a connection.
         0 - unlimited connections
        """
        if self.max_connections == 0:
            return True
        return len(self.connections) < self.max_connections

    @property
    def id(self):
        if self.dagnode:
            return str(self.dagnode.id)
        return None

    def type(self):
        """
        Assistance for the QT windowing toolkit.
        """
        return Connection.Type

    @property
    def color(self):
        """
        Return the 'node color' (background color)
        """
        return self.dagconn.color

    @color.setter
    def color(self, val):
        """
        Return the 'node color' (background color)
        """
        self.dagconn.color = val
        return self.color

    @property
    def bg_color(self):
        """
        Returns the connection background color.

        returns:
            (QColor) - widget background color.
        """
        if not self.is_enabled:
            return QtGui.QColor(*[125, 125, 125])

        if self.is_selected:
            return QtGui.QColor(*[178, 27, 32])

        if self.is_hover:
            return QtGui.QColor(*[243, 118, 111])

        return QtGui.QColor(*self.color)

    @property
    def pen_color(self):
        """
        Returns the connection pen color.

        returns:
            (QColor) - widget pen color.
        """
        return self.bg_color.darker(250)

    @property
    def label_color(self):
        """
        Returns the widget label color.

        returns:
            (QColor) - widget label color.
        """
        if not self.is_enabled:
            return QtGui.QColor(*[50, 50, 50])
        if self.is_selected:
            return QtGui.QColor(*[88, 0, 0])
        return QtGui.QColor(*self._l_color)

    def isInputConnection(self):
        """
        Returns true if the node is an input
        connection in the graph.

        returns:
            (bool) - widget is an input connection.
        """
        if self.is_input == True:
            return True
        return False

    def isOutputConnection(self):
        """
        Returns true if the node is an output
        connection in the graph.

        returns:
            (bool) - widget is an output connection.
        """
        if self.is_input == True:
            return False
        return True

    #- Events ----
    def hoverLeaveEvent(self, event):
        """
        QGraphicsSceneHoverEvent.pos
        """
        if self.isSelected():
            self.setSelected(False)
        QtGui.QGraphicsObject.hoverLeaveEvent(self, event)

    def boundingRect(self):
        """
        Return the bounding rect for the connection (plus selection buffer).
        """
        r = self.radius
        b = self.buffer
        return QtCore.QRectF(-r/2 - b, -r/2 - b, r + b*2, r + b*2)

    def drawRect(self):
        """
        Return the bounding rect for the connection.
        """
        r = self.draw_radius
        b = self.buffer
        return QtCore.QRectF(-r/2 - b, -r/2 - b, r + b*2, r + b*2)

    def shape(self):
        """
        Aids in selection.
        """
        path = QtGui.QPainterPath()
        polyon = QtGui.QPolygonF(self.boundingRect())
        path.addPolygon(polyon)
        return path

    def paint(self, painter, option, widget):
        """
        Draw the connection widget.
        """
        self.is_selected = False
        self.is_hover = False

        # set node selection/hover states
        if option.state & QtGui.QStyle.State_Selected:
            self.is_selected = True

        if option.state & QtGui.QStyle.State_MouseOver:
            self.is_hover = True

        self.setToolTip('%s.%s\n(%.2f, %.2f)' % (self.dagnode.name, self.name, self.pos().x(), self.pos().y()))

        # background
        gradient = QtGui.QLinearGradient(0, -self.draw_radius, 0, self.draw_radius)
        gradient.setColorAt(0, self.bg_color)
        gradient.setColorAt(1, self.bg_color.darker(125))
        
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        painter.setPen(QtGui.QPen(QtGui.QBrush(self.pen_color), 1.5, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QBrush(gradient))

        # draw a circle
        if self.node_shape == 'circle':
            painter.drawEllipse(QtCore.QPointF(0,0), self.draw_radius, self.draw_radius)
        elif self.node_shape == 'pie':
            # pie drawing
            start_angle = 16*90
            if self.isOutputConnection():
                start_angle = start_angle * -1
            painter.drawPie(self.drawRect(), start_angle, 16*180)
        
        # visualize the bounding rect if _debug attribute is true
        if self._debug:
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(self.bg_color, 0.5, QtCore.Qt.DashLine))
            painter.drawRect(self.boundingRect())
