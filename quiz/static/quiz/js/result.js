$(document).ready(function(){
	//棒グラフ用にJSON整形
	function chJSON(data){
		var result = [0,0,0,0];
		for(var i in result){
			result[i] = {'choice_id': parseInt(i)+1 ,'total':0};
		}
		for(var i in data){
			var cid = data[i].choice_id;
			result[cid-1] = {'choice_id':cid,'total':data[i].answerers.length};
		}
		return result;
	}
	
	//結果を棒グラフで表示
	function makeBar(data){
		$("#bar").empty();
		var barWidth = 50;
		var width = (barWidth + 10) * data.length;
		var height = 200;
		var x = d3.scale.linear().domain([0, data.length]).range([0, width]);
		var y = d3.scale.linear().domain([0, d3.max(data, function(d) { return d.total; })]).rangeRound([0, height]);
		// グラフを表示するsvgエリアを作成
		var barDemo = d3.select("#bar")
			.append("svg:svg")
				.attr("width", width)
				.attr("height", height+20);
		//棒グラフの表示
		barDemo.selectAll("rect")
			.data(data)
			.enter()
			.append("svg:rect")
				.attr("x", function(d, i) { return x(i); })
				.attr("y", function(d) { return height - y(d.total); })
				.attr("height", function(d) { return y(d.total); })
				.attr("width", barWidth)
				.attr("fill", "#2d578b");	    
		//投票数を表示    
		barDemo.selectAll("text")
			.data(data)
			.enter()
			.append("svg:text")
				.attr("x", function(d, i) { return x(i) + barWidth; })
				.attr("y", function(d) { return height - y(d.total); })
				.attr("dx", -barWidth/2)
				.attr("dy", "1.2em")
				.attr("text-anchor", "middle")
				.text(function(d) { return d.total;})
				.attr("fill", "white");
		//問題数を表示
		barDemo.selectAll("text.yAxis")
			.data(data)
			.enter()
			.append("svg:text")
				.attr("x", function(d, i) { return x(i) + barWidth; })
				.attr("y", height)
				.attr("dx", -barWidth/2)
				.attr("text-anchor", "middle")
				.attr("style", "font-size: 20; font-family: Helvetica, sans-serif")
				.text(function(d) { return d.choice_id;})
				.attr("transform", "translate(0, 20)")
				.attr("class", "yAxis");
	}

	function makeScore(data){
		for(var i in data){
			var cid = data[i].choice_id;
			var obj = data[i].answerers;
			for(var j in obj){
				var msg = '<tr>';
				//msg = msg + '<td>' + data[i].rank + '</td>';
				msg = msg + '<td>' + obj[j].name + '</td>';
				msg = msg + '<td>' + cid + '</td>';
				msg = msg + '</tr>';
				$("table#result tbody").append(msg);
			}
		}
	}

	$.get(url,
		{
			'type' : 'query',
			'command' : 'answer_summary'
		},
		function(data){
			window.quiz.default_ajax_handler(data);
			if(data.status == 'ok'){
				console.log(data.content);
				makeBar(chJSON(data.content));
				makeScore(data.content);
			}
		}
	);

	$("[data-sticky_column]").stick_in_parent({
		parrent: "[data-sticky_parent]",
		offset_top:70
	});
});
