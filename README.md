Squiggly
==

Squiggly the turtle! A physical programming language for teaching kids programming. Made at MakeMIT 2017.

## Setup
Export the following environment variables before running the Flask server:
```
export FLASK_APP=squiggly
export FLASK_DEBUG=true
```

Then run:
```
pip install -e .
flask run
```

The variable exports and final `flask run` command are in the `start_server.sh` script for convenience. Make sure you `pip install -e .` the first time.

## Block design

Since the Squiggly language is processed visually, the components of the languuage, the blocks, have additional features beyond the cute shapes the users see. Here is a list of all of the different types of blocks Squiggy uses and how they are designed.

### Block localization

In order to infer the location of the blocks from an image, each component contains a string of colors in the top corner of the block. The set of colors includes red, green, and blue in triples. The unique arrangement of these colors identifies the type of block.

Given the positions of the colors, it groups nearby colors on the same block together. This string of colors provides a very easy way to both localize where the block is and determine what the block does.

### Language components

#### Commands

Command blocks are the fundamental building block of the Squiggly language. Example commands include forwards and turn. Command blocks accept arguments by placing the argument blocks adjacent to the command block. For instance, number blocks connect to the right edge of a forwards block to specify how much to move.

Command list:

* forwards(Number amount)
  * move forwards by amount
* turn(Number amount)
  * turn clockwise by amount
* eat(VariableReference x)
  * decrement the variable $x by the amount encoded by x, default to 1

#### Numbers

In addition to the shape string ids, number blocks encode additional information with extra shapes. The identification portion comes first, and then the data component follows.

#### Variables

Variables in Squiggly are food items, like chocolate or gummy worms or marshmallows. Each food item has an implied default numeric value, which can be modified by placing a number block adjacent to the food item.  In contexts that initialize values, the variable is initiated to its associated value. In contexts that operate on variables, such as in `eat` calls, the associated value is the numeric argument that is supplied.

#### Control structures

Control structures contain two sets of shape string ids, analogous start and end curly braces. Control structures enclose commands and optionally/repeatedly perform them.

Control structure list:

* for (VariableReference x)
  * repeat the inner code block using the variable $x as the iteration counter

## License
MIT License
