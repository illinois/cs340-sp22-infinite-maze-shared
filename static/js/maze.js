/*********************************************************************
** Filename: maze.js
** Author: Aiden Nelson and Patrick Crain
** Date: 2022-04-13
** Description: classes for drawing and rendering Maze
*********************************************************************/

const BLOCK_W = 7;//width of a maze block, in cells

class Maze {

    // Remember: Columns are x axis
    //           Rows are y axis

    // Function: constructor
    // Parameters:
    // Description: Creates a game object
    constructor(blockHeight) {
        this.CANVAS_W    = 1000; //width of maze canvas
        this.CANVAS_H    = 600;  //height of maze canvas
        this.BLOCK_C     = Math.floor(BLOCK_W/2)  //halfwidth of maze block
        this.SCALE_P     = 25; //scaling constant for player size

        this.blockHeight  = blockHeight;

        this.camx        = 0;
        this.camy        = 0;
        this.lastx       = 0;
        this.lasty       = 0;
        this.mazeSprite  = null;
        this.default     = null;
        this.player      = null;

        // Dictionary of grids -> one grid = one maze block
        this.grids       = {};
    }

    zoom(blockHeight) {
        this.blockHeight = blockHeight;
        this.renderMaze();
        this.renderPlayer(this.lastx,this.lasty);
    }

    // Function: render
    // Parameters:
    // Description: Sets up game sprites
    renderMaze() {
        let blockHeight = this.blockHeight;
        var firstRender = false;
        if (this.default === null) {
            this.default = paper.project.activeLayer;
            firstRender = true;
        } else {
            this.default.removeChildren();
        }

        // compute some useful constants
        let cellheight   = blockHeight/BLOCK_W;
        let wcells       = this.CANVAS_W/cellheight;
        let hcells       = this.CANVAS_H/cellheight;

        // get the position of the camera relative to the player
        let camrelx      = this.CANVAS_W/2-blockHeight/2+((this.BLOCK_C/BLOCK_W)-this.camx)*blockHeight;
        let camrely      = this.CANVAS_H/2-blockHeight/2+((this.BLOCK_C/BLOCK_W)-this.camy)*blockHeight;

        // determine the minimum and maximum cells visible at the current zoom level
        let gridminx     = this.camx*BLOCK_W-wcells/2;
        let gridmaxx     = this.camx*BLOCK_W+wcells/2;
        let gridminy     = this.camy*BLOCK_W-hcells/2;
        let gridmaxy     = this.camy*BLOCK_W+hcells/2;

        // determine grid coordinates of the topleft-most cell to be rendered
        let renderstartx = BLOCK_W*Math.ceil(gridminx/BLOCK_W)-this.BLOCK_C;
        let renderstarty = BLOCK_W*Math.ceil(gridminy/BLOCK_W)-this.BLOCK_C;

        // actually render the maze
        let rcount = 0;
        for (var y = renderstarty; y < gridmaxy; y += BLOCK_W) {
            for (var x = renderstartx; x < gridmaxx; x += BLOCK_W) {
                let c = x+","+y;
                if (!(c in this.grids)) {
                    continue;  //skip cells that don't exist
                }
                let rx = camrelx+cellheight*x;
                let ry = camrely+cellheight*y;
                let ms = new MazeSprite(this.grids[c],blockHeight,rx,ry);
                rcount += 1;
            }
        }
        document.getElementById("debug").innerHTML = ("Rendered " + rcount + " blocks");

        // render fog around edges of maze
        let BR = this.blockHeight; //fog border radius
        this.renderGradient(0,0,0,BR,"bc","tc");
        this.renderGradient(0,-BR,0,0,"tc","bc");
        this.renderGradient(0,0,BR,0,"cr","cl");
        this.renderGradient(-BR,0,0,0,"cl","cr");

        // finalize the rendering
        if (firstRender) {
            this.renderPlayer(0,0);
        } else {
            view.draw();
        }
    }

    renderGradient(x1,y1,x2,y2,o,d) {

        if (x1 < 0) {
            x1 = this.CANVAS_W + x1;
        }
        if (y1 < 0) {
            y1 = this.CANVAS_H + y1;
        }
        if (x2 <= 0) {
            x2 = this.CANVAS_W + x2;
        }
        if (y2 <= 0) {
            y2 = this.CANVAS_H + y2;
        }

        var rectangle = new Rectangle(new Point(x1, y1), new Point(x2, y2));
        // var shape = new Shape.Ellipse(rectangle);
        var shape = new Shape.Rectangle(rectangle);

        var b = {
            "tl" : shape.bounds.topLeft,
            "tr" : shape.bounds.topRight,
            "bl" : shape.bounds.bottomLeft,
            "br" : shape.bounds.bottomRight,
            "tc" : shape.bounds.topCenter,
            "cr" : shape.bounds.rightCenter,
            "cl" : shape.bounds.leftCenter,
            "bc" : shape.bounds.bottomCenter
        }

        shape.fillColor = {
            gradient: {
                // stops: [[new Color(1,1,1,0), 0.30], [new Color(1,1,1,0.95), 1.0]],
                stops: [[new Color(1,1,1,0), 0.0], [new Color(1,1,1,1), 1.0]],
                radial: false
            },
            origin: b[o],
            destination: b[d]
        };
    }

    renderPlayer(px, py) {
        // Determine whether camera needs to be moved
            // TODO: finish
            let camx = Math.floor((px+this.BLOCK_C)/BLOCK_W);
            let camy = Math.floor((py+this.BLOCK_C)/BLOCK_W);
            if ((camx != this.camx) || (camy != this.camy)) {
                this.camx = camx;
                this.camy = camy;
                this.renderMaze();
            }
            this.lastx = px;
            this.lasty = py;
        // Get player position relative to camera
            let relx = (px-(camx*BLOCK_W))
            let rely = (py-(camy*BLOCK_W))
        // Compute the render position from the player coordinates
            let dx = this.CANVAS_W/2 + relx*(this.blockHeight/BLOCK_W);
            let dy = this.CANVAS_H/2 + rely*(this.blockHeight/BLOCK_W);
        // Create the player layer if necessary, otherwise clear it out
            if (this.player === null) {
                // need to create a new layer for the player sprite
                this.player = new Layer({
                    strokeColor: 'black'
                });
                paper.project.addLayer(this.player);
            } else {
                this.player.removeChildren();
            }
        // Draw the player as a cross shape
            var psize       = this.blockHeight/this.SCALE_P;
            var pp1         = new Path();
            pp1.strokeColor = 'red';
            pp1.strokeWidth = psize/2;
            pp1.add(new Point(dx-psize, dy-psize), new Point(dx+psize, dy+psize));
            var pp2         = new Path();
            pp2.strokeColor = 'red';
            pp2.strokeWidth = psize/2;
            pp2.add(new Point(dx+psize, dy-psize), new Point(dx-psize, dy+psize));
            this.player.addChild(pp1);
            this.player.addChild(pp2);
        // Hide the maze while we redraw the player only
            this.default.visible = false;
            view.draw();
            this.default.visible = true;
    }

    addBlock(rx, ry, geom) {
        if (geom.length % BLOCK_W > 0) {
            alert("WARNING: grid height not a multiple of "+BLOCK_W);
            return false;
        }
        if (geom[0].length % BLOCK_W > 0) {
            alert("WARNING: grid width not a multiple of "+BLOCK_W);
            return false;
        }
        let bh = geom.length/BLOCK_W;
        let bw = geom[0].length/BLOCK_W;
        alert(bw+"x"+bh+" block unit received for "+rx+","+ry);
        for (var by = 0; by < bh; by++) {
            for (var bx = 0; bx < bw; bx++) {
                // determine the coordinates of the new grid
                let ox   = rx + bx*BLOCK_W;
                let oy   = ry + by*BLOCK_W;
                let gkey = ox+","+oy;
                // check if the grid already exists; if so, problem
                if (gkey in this.grids) {
                    alert("WARNING: grid already exists at "+gkey);
                    continue;
                }
                // add a new grid for every 7x7 block
                var grid = new Grid(BLOCK_W, BLOCK_W)
                for (var y = 0; y < BLOCK_W; y++) {
                    for (var x = 0; x < BLOCK_W; x++) {
                        grid.cells[x][y] = parseInt(geom[y+by*BLOCK_W][x+bx*BLOCK_W], 16);
                    }
                }
                // add the grid to the grid dictionary
                this.grids[gkey] = grid;
            }
        }
        // re-render the maze
        this.renderMaze();
    }
}

class MazeSprite {

    constructor(grid, size, xCoord, yCoord) {
        this.drawGrid(grid, size, xCoord, yCoord);
    }

    // Function: drawCell
    // Parameters: cell object, size of cell in pixels, x & y coordinates of cell
    // Description: Draw graphical representation of cell
    drawCell(c, size, xCoord, yCoord) {

        // Thickness of lines that draw the cells
        var lineThickness = 0.15 * size;

        // Extra length added to lines in order to make corners look nice
        var cornerFlushing = lineThickness/2;

        var x1 = xCoord;
        var y1 = yCoord;
        var x2 = xCoord + size;
        var y2 = yCoord + size;

        let wallNorth = c & 8;
        let wallEast  = c & 4;
        let wallSouth = c & 2;
        let wallWest  = c & 1;

        if (wallNorth) { // Get these lines horizontal
            var northPath = new Path();
            northPath.strokeWidth = lineThickness;
            northPath.strokeColor = 'purple';
            northPath.add(new Point(x2 + cornerFlushing, y1), new Point(x1 - cornerFlushing, y1));
        }
        if (wallWest) {
            var westPath = new Path();
            westPath.strokeColor = 'purple';
            westPath.strokeWidth = lineThickness;
            westPath.add(new Point(x1, y1), new Point(x1, y2));
        }
        if (wallSouth) {
            var southPath = new Path();
            southPath.strokeColor = 'purple';
            southPath.strokeWidth = lineThickness;
            southPath.add(new Point(x1 - cornerFlushing, y2), new Point(x2 + cornerFlushing, y2));
        }
        if (wallEast) {
            var eastPath = new Path();
            eastPath.strokeColor = 'purple';
            eastPath.strokeWidth = lineThickness;
            eastPath.add(new Point(x2, y1), new Point(x2, y2));
        }
    }


    // Function: drawGrid
    // Parameters: grid object, size of grid in pixels lengthwise, x & y coordinates of grid upper left corner
    // Description: Draw graphical representation of grid
    drawGrid(grid, size, xCoord, yCoord) {
        // Calculate bottom left of cell
        var cellSize    = size / grid.rows;

        // Drawing begins from bottom left corner, one column at a time
        for (var x = 0; x < grid.columns; x++) {
            for (var y = 0; y < grid.rows; y++) {
                let canvasX = xCoord + (cellSize * x);
                let canvasY = yCoord + (cellSize * y);
                this.drawCell(grid.cells[x][y], cellSize, canvasX, canvasY);
            }
        }
    }
}

class Grid {

    constructor(columns, rows) {
        this.rows    = rows;
        this.columns = columns;
        this.cells   = new Array(this.columns)
        for (var x = 0; x < this.cells.length; x++) {
            this.cells[x] = new Array(this.rows);
        }
    }

}
