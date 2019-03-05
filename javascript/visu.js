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



// Add legend
var divLegendDates = d3.select("#divLegendDates");

divLegendDates.append("p")
    .html("Friend added in")
    .style("text-align","center")
    .style("font-size","20px");

var listDates = divLegendDates.append("ul");

var divLegendSizes = d3.select('#divLegendSizes');

divLegendSizes.append("p")
    .html("Number of pages followed")
    .style("text-align","center")
    .style("font-size","20px");

var divLegendConnection = d3.select('#divLegendConnection');

divLegendConnection.append("p")
    .html("— Are friends with each other")
    .style("text-align","center")
    .style("font-size","20px");



// -----------------------------------------------------------------------------

function drawGraph(nodes, links) {

  d3.selectAll("g").remove()
  // d3.selectAll("circle").remove()

  //add encompassing group for the zoom
  var g = svg.append("g")
      .attr("class", "everything");


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
        tooltip.html(d.name + "<br/>" + d.size)
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

function selectElements(nodes, nbElements){

  var sizeCount = d3.nest()
    .key(function(d) { return d.size})
    .entries(nodes);

  sizeCount.sort(function(a,b) { return +a.key - +b.key })

  var len = sizeCount.length/nbElements

  var newData = sizeCount.map(function(v) {return +v.key;});

  var sizes = [];

  for   (i=0; i < nbElements; i++) {
    var index = Math.round(i*len);
    var key = newData[index];
    sizes.push(key)
  }
  var last_key = newData[len*nbElements - 1];
  sizes.push(last_key)

  return sizes;
}

function addLegendDates(nodes){

  var datesCount = d3.nest()
    .key(function(d) { return d.timestamp; })
    .rollup(function(v) { return v.length; })
    .entries(nodes);

  datesCount.sort(function(a,b){
    return a.key.localeCompare(b.key);
  });

  var entries = listDates.selectAll("li")
    .data(datesCount)
    .enter()
    .append("li");


  // append rectangle and text:
  entries.append("span")
    .attr("class","rect")
    .style("background-color", function(d) { return color(+d.key); })

  entries.append("span")
    .attr("class","label")
    .html(function(d) { return d.key; })

}

function addLegendSizes(){


  var height = 300
  var width = 270
  var svg = d3.select("#divLegendSizes")
    .append("svg")
      .attr("width", width)
      .attr("height", height)

  // Add legend: circles
  // var valuesToShow = selectElements(nodes, 5);
  var valuesToShow = [5, 50, 100, 250, 1000]
  var xCircle = 75
  var xLabel = 200
  var yCircle = 20
  var lastyCircle = 0

  valuesToShow.forEach(function(d, i){
    svg
      .append("circle")
        .attr("class", "circlesLegend")
        .attr("cx", xCircle)
        .attr("cy", yCircle + Math.sqrt(d) + lastyCircle )
        .attr("r", Math.sqrt(d))
        .style("fill", "black")
        .attr("stroke", "black")

    svg
      .append("line")
        .attr("class", "linesLegend")
        .attr('x1', xCircle + Math.sqrt(d) )
        .attr('x2', xLabel)
        .attr('y1', yCircle + Math.sqrt(d) + lastyCircle)
        .attr('y2', yCircle + Math.sqrt(d) + lastyCircle)
        .attr('stroke', 'black')
        .style('stroke-dasharray', ('2,2'))

  svg
    .append("text")
      .attr("class", "textLegend")
      .attr('x', xLabel)
      .attr('y', yCircle + Math.sqrt(d) + lastyCircle)
      .text( d)
      .style("font-size", 7)
      .attr('alignment-baseline', 'middle')

  lastyCircle += 2*Math.sqrt(d) + yCircle
  console.log(lastyCircle)
  })
}


// -----------------------------------------------------------------------------

var fichierSelectionne = document.getElementById('real_file_button').files[0];
console.log(fichierSelectionne);

function update(file){
  d3.json(file, function(error, graph) {
    if (error) throw error;


    var selectedCategory = d3.select('input[name="category"]:checked').property("value");

    var links = graph['links_' + selectedCategory];
    var nodes = graph['nodes_' + selectedCategory];

    drawGraph(nodes, links);
    addLegendDates(nodes);
    addLegendSizes();

    //radio button
    d3.selectAll(("input[name='category']")).on("change", function() {
        var links_new = graph['links_' + this.value];
        var nodes_new = graph['nodes_' + this.value];

        console.log(links_new)

        drawGraph(nodes_new, links_new);
        addLegendDates(nodes);
        // addLegendSizes();

    });



  });
};

update("graph.json");

