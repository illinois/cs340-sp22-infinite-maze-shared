// Make the paper scope global, by injecting it into window:
paper.install(window);

var zoomlevel = 200;
var maze      = new Maze(zoomlevel); //CANVAS_H = 600 -> 3 blocks high

// Upon window loading
window.onload = function() {
  paper.setup('myCanvas');
}

zoomMaze = () => {
  zoomlevel /= 2;
  if (zoomlevel < 20) {
    zoomlevel = 200
  }
  maze.zoom(zoomlevel);
}


grid     = {};
requestX = -3;
requestY = -3;
x        = 0;
y        = 0;

minX = 0, maxX = 0, minY = 0, maxY = 0;

requestGrid = (requestX, requestY) => {
  console.log(`RequestGrid(${requestX}, ${requestY})`);
  $.get("/generateSegment")
  .done(function (data) {
    let geom = data.geom;
    for (let curY = 0; curY < geom.length; curY++) {
      let g = geom[curY];

      for (let curX = 0; curX < g.length; curX++) {
        let c = g[curX];

        if (!grid[curX + requestX]) { grid[curX + requestX] = {} }
        grid[requestX + curX][requestY + curY] = c;

        if (requestX + curX < minX) { minX = requestX + curX; }
        if (requestX + curX > maxX) { maxX = requestX + curX; }
        if (requestY + curY < minY) { minY = requestY + curY; }
        if (requestY + curY > maxY) { maxY = requestY + curY; }
      }
    }

    console.log(grid);
    // renderGrid();

    maze.addBlock(requestX, requestY, geom);
  })
  .fail(function (data) {
    $("#maze").html(`<hr><h3>Error</h3><p>${JSON.stringify(data)}</p>`);
  })
};

expandGrid = (dX, dY) => {
  if (dX == 1)  { requestGrid(x, y - 3); }
  if (dX == -1) { requestGrid(x - 6, y - 3); }
  if (dY == 1)  { requestGrid(x - 3, y); }
  if (dY == -1) { requestGrid(x - 3, y - 6); }
};

move = (dX, dY) => {
  if (!grid[x] || !grid[x][y]) {
    return false;  //ignore key events if our current maze section isn't loaded
  }

  x          += dX;
  y          += dY;

  if (!grid[x] || !grid[x][y]) {
    console.log("Expand Grid!");
    expandGrid(dX, dY);
  }

  maze.renderPlayer(x,y);
};

document.onkeydown = (e) => {
  let sq        = parseInt(grid[x][y], 16);
  let wallNorth = sq & 8;
  let wallEast  = sq & 4;
  let wallSouth = sq & 2;
  let wallWest  = sq & 1;
  
  if      (e.keyCode == '38' && !wallNorth) { move(0 , -1); }
  else if (e.keyCode == '40' && !wallSouth) { move(0 ,  1); }
  else if (e.keyCode == '37' && !wallWest)  { move(-1,  0); }
  else if (e.keyCode == '39' && !wallEast)  { move(1 ,  0); }
  else if (e.keyCode == '90')               { zoomMaze(); }
};

$(() => {
  requestGrid(-3, -3);
});
