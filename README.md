# extended-persistence-metric-graph
Implements an interactive metric graph editor with interactive extended persistence barcode computation

## Install
`pip3 install -r requirements.txt`

(requirements are simply numpy for computations and pygame for the rendering)

## Example
run `python3 main.py -g loops.g`

## Commands

- Left click on blank: create a node
- Left click on a node and stay pressed: add an edge (release click on the target node)

- Right click (anywhere): Set the `base_point` to compute the barcode (to the closest point on the graph)
- hit `w` to save the current graph to the file given to -g argument (or to default)

## Remarks:
- Graph has to be connected to compute barcode
- The computed reeb graph (associated to the sublevelset of the distance function to the base_point) is displayed in red (only the additional points)
- The base_point is in green
