// Make the paper scope global, by injecting it into window:
paper.install(window);

var zoomlevel = 200;
var maze = new Maze(zoomlevel); //CANVAS_H = 600 -> 3 blocks high

// Generate a random user ID for now
const getRandomLetters = (length = 1) => Array(length).fill().map(e => String.fromCharCode(Math.floor(Math.random() * 26) + 65)).join('');
var uid = getRandomLetters(8);

// $( function ) runs once the DOM is ready:
$(() => {
  paper.setup("myCanvas");
  requestGrid(-3, -3);
});

zoomMaze = () => {
  zoomlevel /= 2;
  if (zoomlevel < 20) {
    zoomlevel = 200;
  }
  maze.zoom(zoomlevel);
};

computeUnit = (requestX, requestY) => {
  return {
    col: Math.floor( ((requestX + BLOCK_C) / BLOCK_W) + 0.5 ),
    row: Math.floor( ((requestY + BLOCK_C) / BLOCK_W) + 0.5 ),
  };
};

grid = {};
requestX = -3;
requestY = -3;
x = 0;
y = 0;

(minX = 0), (maxX = 0), (minY = 0), (maxY = 0);

requestGrid = (requestX, requestY) => {
  console.log(`RequestGrid(${requestX}, ${requestY})`);
  $.get("/generateSegment", computeUnit(requestX, requestY))
    .done(function (data) {
      // get origin information for the maze segment
      var ox = data["originX"] ?? 0;
      var oy = data["originY"] ?? 0;

      // adjust the request's x and y based on segment origin
      let gridUnit = computeUnit(requestX, requestY);
      let ry = (gridUnit.row * BLOCK_W) - 3;
      let rx = (gridUnit.col * BLOCK_W) - 3;

      // verify we don't have a multiblock segment with no origin
      let geom = data["geom"];
      if (!(geom.length == BLOCK_W && geom[0].length == BLOCK_W)) {
        if (!("originX" in data && "originY" in data)) {
          alert(
            "WARNING: origin X and Y not specified for multiblock maze segment"
          );
          return false;
        }
      }

      // populate the local grid as necessary
      for (let curY = 0; curY < geom.length; curY++) {
        let g = geom[curY];

        for (let curX = 0; curX < g.length; curX++) {
          let c = g[curX];

          if (!grid[curX + rx]) {
            grid[curX + rx] = {};
          }
          grid[rx + curX][ry + curY] = c;

          if (rx + curX < minX) {
            minX = rx + curX;
          }
          if (rx + curX > maxX) {
            maxX = rx + curX;
          }
          if (ry + curY < minY) {
            minY = ry + curY;
          }
          if (ry + curY > maxY) {
            maxY = ry + curY;
          }
        }
      }

      console.log(grid);

      // actually add the block to the grid for rendering purposes
      maze.addBlock(rx, ry, geom);
    })
    .fail(function (data) {
      $("#maze").html(`<hr><h3>Error</h3><p>${JSON.stringify(data)}</p>`);
    });
};

expandGrid = (dX, dY) => {
  if (dX == 1) {
    requestGrid(x, y - 3);
  }
  if (dX == -1) {
    requestGrid(x - 6, y - 3);
  }
  if (dY == 1) {
    requestGrid(x - 3, y);
  }
  if (dY == -1) {
    requestGrid(x - 3, y - 6);
  }
};

move = (dX, dY) => {
  if (!grid[x] || !grid[x][y]) {
    return false; //ignore key events if our current maze section isn't loaded
  }

  x += dX;
  y += dY;

  if (!grid[x] || !grid[x][y]) {
    console.log("Expand Grid!");
    expandGrid(dX, dY);
  }

  maze.renderPlayer(x, y);
  maze.renderMaze();
};

document.onkeydown = (e) => {
  let sq = parseInt(grid[x][y], 16);
  let wallNorth = sq & 8;
  let wallEast = sq & 4;
  let wallSouth = sq & 2;
  let wallWest = sq & 1;

  if (e.keyCode == "38" && !wallNorth) {
    move(0, -1);
    crumbs["steps"] += "n";
  } else if (e.keyCode == "40" && !wallSouth) {
    move(0, 1);
    crumbs["steps"] += "s";
  } else if (e.keyCode == "37" && !wallWest) {
    move(-1, 0);
    crumbs["steps"] += "w";
  } else if (e.keyCode == "39" && !wallEast) {
    move(1, 0);
    crumbs["steps"] += "e";
  } else if (e.keyCode == "90") {
    zoomMaze();
  }
};

// player breadcrumb update heartbeat
var crumbs = {
  "user"  : uid,
  "x"     : x,
  "y"     : y,
  "steps" : ""
};

var players = {};

movePlayers = () => {
  for (const [k, p] of Object.entries(players)) {
    if (p["steps"].length == 0) {
      continue;
    }
    let dir = p["steps"][0];
    p["steps"] = p["steps"].substring(1);
    if (dir == "n") p["y"] = parseInt(p["y"]) - 1;
    if (dir == "s") p["y"] = parseInt(p["y"]) + 1;
    if (dir == "w") p["x"] = parseInt(p["x"]) - 1;
    if (dir == "e") p["x"] = parseInt(p["x"]) + 1;
  }
  maze.renderMaze();
  // document.getElementById("debug").innerHTML = JSON.stringify(players);

  setTimeout(() => {
    movePlayers();
  }, 100);
}

sendHeartbeat = () => {
  $.post("/heartbeat", crumbs)
    .done(function (data) {
      for (const [k, p] of Object.entries(data)) {
        if (!(k in players)) {
          players[k] = p;
        }
        else if (p["time"] > players[k]["time"]) {
          players[k] = p;
        }
      }
      // maze.renderMaze();
    });
  crumbs = {
    "user"  : uid,
    "x"     : x,
    "y"     : y,
    "steps" : ""
  };
  setTimeout(() => {
    sendHeartbeat();
  }, 1000);
}

setTimeout(() => {
  sendHeartbeat();
}, 1000);

setTimeout(() => {
  movePlayers();
}, 1000);

