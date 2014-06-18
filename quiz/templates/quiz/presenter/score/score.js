<style type="text/css">
	th{
		text-align: center;
		font-size: 16px;
	}
	td{
		text-align: center;
		vertical-align: top;
		font-size: 20px;
	}
</style>

<script type="text/javascript">
	$(document).ready(function(){
		//ランキング表作成
		function makeRanking(data){
			for(var i in data){
				var msg;
				if(data[i].is_you){
					msg = '<tr class="success">';
				} else {
					msg = '<tr>';
				}
				msg = msg + '<td>' + data[i].rank + '</td>';
				msg = msg + '<td>' + data[i].name + '</td>';
				msg = msg + '<td>' + data[i].score + '</td>';
				msg = msg + '</tr>';
				$("table#ranking tbody").append(msg);
			}
		}

		//GET後ランキング表を表示
		$.get('{% url 'lobby_show' lobby.pk %}',
			{
				'type' : 'query',
				'command' : 'score_list'
			},
			function(data){
				window.quiz.default_ajax_handler(data);
				if(data.status == 'ok'){
					makeRanking(data.content);
				}
		});
	});
</script>