
function getData(){

    var data = Array()

    var versions = d3.selectAll("ul.version").each(function() {

        data.push({
            'label': d3.select(this).attr('id'),
            'total': d3.select(this).select('li em.n_apps').html(),
            'date': d3.select(this).select('li em.release_date').html(),
        });
    });

    return data.reverse();
}

function drawBaseGraph(containerId, data){

    var margin = ({top: 20, right: 30, bottom: 30, left: 40});
      
    var svg = d3.select('#'+containerId).append("svg")
        .attr("class","chart")
        .attr("width", '100%')
        .attr("height", '200px')
        .attr('transform', 'translate(' + margin.left + ',0)');

    var width = $('#'+containerId).find('svg').width();
    var height = $('#'+containerId).find('svg').height();

     var x = d3.scaleTime()
        .domain(d3.extent([new Date(data[0].date), new Date(data[data.length - 1].date)]))
        .range([margin.left, width - margin.left - margin.right]);
    

     var y = d3.scaleLinear()
       .domain([0, data[data.length - 1].total])
       .range([height - margin.top-margin.bottom,margin.bottom + margin.top]);

     var xAxis = g => g
        .attr("class", "x axis")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%m/%d/%Y')).tickSizeOuter(0))

      var yAxis = g => g
        .attr("class","y axis")
        .attr('transform','translate('+margin.left+',0)')
        .call(d3.axisLeft(y))
        .call(g => g.select(".domain").remove());

     svg.append("g")
        .call(xAxis)
      
     svg.append("g")
        .call(yAxis)
       

      var line = d3.line()
        .x(function(d,i) { 
            return x(new Date(d.date));
         })
        .y(function(d) { 
             d.total = parseInt(d.total);
             return y(d.total); 
        });

    var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);


     svg.selectAll("line.y")
        .data(y.ticks())
        .enter().append("line")
        .attr("class", "dashed")
        .attr("x1", margin.left)
        .attr("x2", width-margin.right-margin.left)
        .attr("y1", y)
        .attr("y2", y)
        .style("stroke", "#ccc");

      svg.append("svg:path")
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("stroke-linejoin", "round")
      .attr("stroke-linecap", "round")
      .attr("d", line(data));

    svg.append("g")
      .attr("stroke-width", 1.5)
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
    .selectAll("g")
    .data(data)
    .join("g")
      .attr("transform", d => `translate(${x(new Date(d.date))},${y(d.total)})`)
      .call(g => g.append("circle")
          .attr("fill", "steelblue")
          .attr("r", 3))
           .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", 1);
            div.html(d.total + " apps")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
          })

      .call(g => g.append("text")
          .attr("dy", "-1.0em")
          .attr("dx", "0.5em")
          .text(d => d.label));
     
  }


drawBaseGraph('apps_evolution', getData());

