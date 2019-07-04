function get_data(){
    var data = Array();
    var total = 0;

    d3.selectAll("tr[data-lang]").each(function() {
        
        const code = d3.select(this).select('td[data-code]').attr('data-code')

        data.push({
            'name': d3.select(this).attr('data-lang'),
            'code': code
        });

        total += parseInt(code);
    });

    data.forEach(function(element){
        element['perc'] = parseInt(Math.round(100*(element.code/total)));
    });

    return {'languages' : data };
}
    const width = 350;
    const height = 350;
    const radius = Math.min(width, height) / 2;

    const svg = d3.select("#pie")
        .append("svg")
            .attr("width", width)
            .attr("height", height)
        .append("g")
            .attr("transform", `translate(${width / 2}, ${height / 2})`);

    

    const color = d3.scaleOrdinal(["#EF5350","#0D47A1", "#039be5"]);

    const pie = d3.pie()
        .value(d => d.code)
        .sort(null);

    const arc = d3.arc()
        .innerRadius(radius - 50)
        .outerRadius(radius);


    function arcTween(a) {
        const i = d3.interpolate(this._current, a);
        this._current = i(1);
        return (t) => arc(i(t));
    }
 

    var data = get_data();

svg
  .selectAll('mySlices')
  .data(pie(data['languages']))
  .enter()
  .append('path')
    .attr('d', arc)
    .attr("fill", (d, i) => color(i))
    .style("opacity", 0.7)

// Now add the annotation. Use the centroid method to get the best coordinates
svg
  .selectAll('mySlices')
  .data(pie(data['languages']))
  .enter()
  .append('text')
  .text(function(d){ return  d.data.name + "("+d.data.perc+"%)"})
  .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")";  })
  .style("text-anchor", "middle")
  .style("font-size", 14)




    function update(val = this.value) {
        // Join new data
        const path = svg.selectAll("path")
            .data(pie(data[val]));

        // Update existing arcs
        path.transition().duration(200).attrTween("d", arcTween);

        // Enter new arcs
        path.enter().append("path")
            .attr("fill", (d, i) => color(i))
            .attr("d", arc)
            .attr("stroke", "white")
            .attr("stroke-width", "6px")
            .each(function(d) { this._current = d; });
     }

//        update("languages");
