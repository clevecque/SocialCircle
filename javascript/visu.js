var svg = d3.select("svg"),
  width = +svg.attr("width"),
  height = +svg.attr("height");

var f = d3.format(".1f");

var color = d3.scaleOrdinal(d3.schemeCategory10);
// var radius = 3;

var alpha = 10; // alpha est un facteur pour mettre a l echelle visuellement

// Define the div for the tooltip
var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

var simulation = d3.forceSimulation()
  .force("link", d3.forceLink().id(function(d) {
    return d.id;
  }).distance(function(d) {
    // c'est ici qu'on calcule la distance. On peut essayer d'autres fonctions (log, etc)
    return height * d.distance * alpha // alpha est un facteur pour mettre a l echelle visuellement
  }).strength(0.1))
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius(function(d) { return Math.sqrt(d.size) + 0.5; }));

//add encompassing group for the zoom
var g = svg.append("g")
    .attr("class", "everything");

// -----------------------------------------------------------------------------

function drawGraph(nodes, links) {

  d3.selectAll("line").remove()
  d3.selectAll("circle").remove()



  var link = g.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("stroke-width", d => (
      +d.relation === 0 ? 0 : 0.2)
    )
    .style("stroke-opacity", 0);

  var node = g.append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(nodes)
    .enter().append("g")

  var circles = node.append("circle")
    // on définit ici le rayon du cercle, racine carrée pour ne pas que ça explose
    .attr("r", d => {return Math.sqrt(d.size)})
    .attr("fill", d => {return color(d.timestamp)})
    // on ajoute les légendes
    .on("mouseover.tooltip", function(d) {
        tooltip.transition()
            .duration(200)
            .style("opacity", .9);
        tooltip .html(d.name)
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
        })
    .on("mouseout.tooltip", function() {
        tooltip.transition()
            .style("opacity", 0);
    })
    .on('mouseover.fade', highlight(1, 'on'))
    .on('mouseout.fade', highlight(0, 'off'))
    .on("mousemove", function() {
      tooltip.style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY + 10) + "px");
    });


  //add drag capabilities
  var drag_handler = d3.drag()
    .on("start", drag_start)
    .on("drag", drag_drag)
    .on("end", drag_end);

  drag_handler(node);


  //add zoom capabilities
  var zoom_handler = d3.zoom()
      .on("zoom", zoom_actions);

  zoom_handler(svg);


  simulation
    .nodes(nodes)
    .on("tick", ticked);

  simulation.force("link")
    .links(links);

  function ticked() {
    link
      .attr("x1", function(d) {
        return d.source.x;
      })
      .attr("y1", function(d) {
        return d.source.y;
      })
      .attr("x2", function(d) {
        return d.target.x;
      })
      .attr("y2", function(d) {
        return d.target.y;
      });

    node
      .attr("transform", function(d) {
        return "translate(" + d.x + "," + d.y + ")";
      })
  }


  //Drag functions
  //d is the node
  function drag_start(d) {
   if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
  }

  //make sure you can't drag the circle outside the box
  function drag_drag(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function drag_end(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    // d.fx = null;
    // d.fy = null;
  }

  function releasenode(d) {
    d.fx = null;
    d.fy = null;
  }

  //Zoom functions
  function zoom_actions(){
      g.attr("transform", d3.event.transform)
  }

  const linkedByIndex = {};

  links.forEach(function(d) {
      linkedByIndex[`${d.source.index},${d.target.index}`] = 1;
  });

  function isConnected(a, b) {
    return linkedByIndex[`${a.index},${b.index}`] || linkedByIndex[`${b.index},${a.index}`] || a.index === b.index;
  }

  function highlight(opacity, toggle) {
    return d => {
      node.style('stroke-opacity', function (o) {
        if (toggle === 'on') {
          // condition ? value-if-true : value-if-false
          const thisOpacity = isConnected(d, o) ? opacity : 0;
          this.setAttribute('fill-opacity', thisOpacity);
          return thisOpacity;
        } else {
          this.setAttribute('fill-opacity', 1);
          return 1;
        }
      });

      link.style('stroke-opacity', o => (o.source === d || o.target === d ? opacity : 0));

    };
  }
}


// -----------------------------------------------------------------------------


d3.json("graph.json", function(error, graph) {
  if (error) throw error;


  var selectedCategory = d3.select('input[name="category"]:checked').property("value");

  var links = graph['links_' + selectedCategory];
  var nodes = graph['nodes_' + selectedCategory];

  drawGraph(nodes, links);

  //radio button
  d3.selectAll(("input[name='category']")).on("change", function() {
      var links_new = graph['links_' + this.value];
      var nodes_new = graph['nodes_' + this.value];

      console.log(links_new)

      drawGraph(nodes_new, links_new);
  });



});
