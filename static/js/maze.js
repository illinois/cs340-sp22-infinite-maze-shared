/*********************************************************************
** Filename: maze.js
** Author: Aiden Nelson and Patrick Crain
** Date: 2022-04-13
** Description: classes for drawing and rendering Maze
*********************************************************************/

const BLOCK_W = 7; //width of a maze block, in cells
const BLOCK_C = Math.floor(BLOCK_W/2)  //halfwidth of maze block

class Maze {

    // Remember: Columns are x axis
    //           Rows are y axis

    // Function: constructor
    // Parameters:
    // Description: Creates a game object
    constructor(blockHeight) {
        this.CANVAS_W    = 1000; //width of maze canvas
        this.CANVAS_H    = 600;  //height of maze canvas
        this.SCALE_P     = 25; //scaling constant for player size

        this.blockHeight  = blockHeight;

        this.camx        = 0;
        this.camy        = 0;
        this.lastx       = 0;
        this.lasty       = 0;
        this.mazeSprite  = null;
        this.default     = null;
        this.player      = {};

        // Dictionary of grids -> one grid = one maze block
        this.grids       = {};
    }

    zoom(blockHeight) {
        this.blockHeight = blockHeight;
        this.renderPlayer(this.lastx,this.lasty);
        this.renderMaze();
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
        }
        this.default.removeChildren();

        // compute some useful constants
        let cellheight   = blockHeight/BLOCK_W;
        let wcells       = this.CANVAS_W/cellheight;
        let hcells       = this.CANVAS_H/cellheight;

        // get the position of the camera relative to the player
        let camrelx      = this.CANVAS_W/2-blockHeight/2+((BLOCK_C/BLOCK_W)-this.camx)*blockHeight;
        let camrely      = this.CANVAS_H/2-blockHeight/2+((BLOCK_C/BLOCK_W)-this.camy)*blockHeight;

        // determine the minimum and maximum cells visible at the current zoom level
        let gridminx     = this.camx*BLOCK_W-wcells/2;
        let gridmaxx     = this.camx*BLOCK_W+wcells/2;
        let gridminy     = this.camy*BLOCK_W-hcells/2;
        let gridmaxy     = this.camy*BLOCK_W+hcells/2;

        // determine grid coordinates of the topleft-most cell to be rendered
        let renderstartx = BLOCK_W*Math.ceil(gridminx/BLOCK_W)-BLOCK_C;
        let renderstarty = BLOCK_W*Math.ceil(gridminy/BLOCK_W)-BLOCK_C;

        // render the players
        if (firstRender) {
            this.renderPlayer(0,0);
        } else {
            for (const [k, p] of Object.entries(players)) {
              maze.renderPlayer(p["x"], p["y"], k);
            }
        }

        // actually render the maze
        let rcount = 0;
        for (var y = renderstarty; y < gridmaxy; y += BLOCK_W) {
            for (var x = renderstartx; x < gridmaxx; x += BLOCK_W) {
                let c = x+","+y;
                if (!(c in this.grids)) {
                    continue;  //skip cells that don't exist
                }
                
                let gridUnit = computeUnit(x, y)
                let gridString = gridUnit["col"] + "," + gridUnit["row"];
                let gridColor = gridColors[gridString];

                if (gridColor[0] != "#") {
                    gridColor = "#" + gridColor;
                }
                
                let rx = camrelx+cellheight*x;
                let ry = camrely+cellheight*y;
                let ms = new MazeSprite(this.grids[c],blockHeight,rx,ry, gridColor);
                rcount += 1;
            }
        }
        //document.getElementById("debug").innerHTML = ("Rendered " + rcount + " blocks");

        // render fog around edges of maze
        let BR = this.blockHeight; //fog border radius
        this.renderGradient(0,0,0,BR,"bc","tc");
        this.renderGradient(0,-BR,0,0,"tc","bc");
        this.renderGradient(0,0,BR,0,"cr","cl");
        this.renderGradient(-BR,0,0,0,"cl","cr");

        view.draw();
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

    renderPlayer(px, py, pid="me") {
        if (pid == uid) {
            //current player is rendered as "me", don't render twice
            return;
        }
        // Determine whether camera needs to be moved
            var rerender = false;
            if (pid == "me") {
                let camx = Math.floor((px+BLOCK_C)/BLOCK_W);
                let camy = Math.floor((py+BLOCK_C)/BLOCK_W);
                if ((camx != this.camx) || (camy != this.camy)) {
                    this.camx = camx;
                    this.camy = camy;
                    rerender = true;
                }
                this.lastx = px;
                this.lasty = py;
            }
        // Get player position relative to camera
            let relx = (px-(this.camx*BLOCK_W))
            let rely = (py-(this.camy*BLOCK_W))
        // Compute the render position from the player coordinates
            let dx = this.CANVAS_W/2 + relx*(this.blockHeight/BLOCK_W);
            let dy = this.CANVAS_H/2 + rely*(this.blockHeight/BLOCK_W);
        // Create the player layer if necessary, otherwise clear it out
            if (!(pid in this.player)) {
                // need to create a new layer for the player sprite
                this.player[pid] = new Layer({
                    strokeColor: 'black'
                });
                paper.project.addLayer(this.player[pid]);
            } else {
                this.player[pid].removeChildren();
            }
        // Draw the player as a cross shape
            var pc = (pid == "me") ? userColorHex : players[pid].color

            var psize       = this.blockHeight/this.SCALE_P;
            if (pid !== "me") { psize *= 0.75; }

            let drawX = (dx, dy, psize, pc) => {
                let pp1         = new Path();
                pp1.strokeColor = pc;
                pp1.strokeWidth = psize/2;
                pp1.add(new Point(dx-psize, dy-psize), new Point(dx+psize, dy+psize));
                let pp2         = new Path();
                pp2.strokeColor = pc;
                pp2.strokeWidth = psize/2;
                pp2.add(new Point(dx+psize, dy-psize), new Point(dx-psize, dy+psize));
                this.player[pid].addChild(pp1);
                this.player[pid].addChild(pp2);    
            };
            drawX(dx, dy, psize, pc);

            if (players[pid] && players[pid].steps) {
                for (let step of players[pid].steps) {
                    psize *= 0.9;

                    px = step[0]
                    py = step[1]
    
                    relx = (px-(this.camx*BLOCK_W))
                    rely = (py-(this.camy*BLOCK_W))
    
                    dx = this.CANVAS_W/2 + relx*(this.blockHeight/BLOCK_W);
                    dy = this.CANVAS_H/2 + rely*(this.blockHeight/BLOCK_W);
    
                    drawX(dx, dy, psize, pc);
                }    
            }

        // Rerender the maze if necessary
            if (rerender) {
                this.renderMaze();
            }
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
        // alert(bw+"x"+bh+" block unit received for "+rx+","+ry);
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

    constructor(grid, size, xCoord, yCoord, gridColor) {
        this.drawGrid(grid, size, xCoord, yCoord, gridColor);
    }

    // Function: drawCell
    // Parameters: cell object, size of cell in pixels, x & y coordinates of cell
    // Description: Draw graphical representation of cell
    drawCell(c, size, xCoord, yCoord, gridColor) {

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
            northPath.strokeColor = gridColor;
            northPath.strokeWidth = lineThickness;
            northPath.add(new Point(x2 + cornerFlushing, y1), new Point(x1 - cornerFlushing, y1));
        }
        if (wallWest) {
            var westPath = new Path();
            westPath.strokeColor = gridColor;
            westPath.strokeWidth = lineThickness;
            westPath.add(new Point(x1, y1), new Point(x1, y2));
        }
        if (wallSouth) {
            var southPath = new Path(); 
            southPath.strokeColor = gridColor;
            southPath.strokeWidth = lineThickness;
            southPath.add(new Point(x1 - cornerFlushing, y2), new Point(x2 + cornerFlushing, y2));
        }
        if (wallEast) {
            var eastPath = new Path();
            eastPath.strokeColor = gridColor;
            eastPath.strokeWidth = lineThickness;
            eastPath.add(new Point(x2, y1), new Point(x2, y2));
        }
    }


    // Function: drawGrid
    // Parameters: grid object, size of grid in pixels lengthwise, x & y coordinates of grid upper left corner
    // Description: Draw graphical representation of grid
    drawGrid(grid, size, xCoord, yCoord, gridColor) {
        // Calculate bottom left of cell
        var cellSize    = size / grid.rows;

        // Drawing begins from bottom left corner, one column at a time
        for (var x = 0; x < grid.columns; x++) {
            for (var y = 0; y < grid.rows; y++) {
                let canvasX = xCoord + (cellSize * x);
                let canvasY = yCoord + (cellSize * y);
                this.drawCell(grid.cells[x][y], cellSize, canvasX, canvasY, gridColor);
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
