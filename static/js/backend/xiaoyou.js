 // 基于准备好的dom，初始化echarts实例
 var myChart = echarts.init(document.getElementById('content'));
                    
 // 指定图表的配置项和数据
 var option = {
     title: {
         text: '文章發布數'
     },
     tooltip: {},
     legend: {
         data:['文章數量']
     },
     xAxis: {
         data: ["FB","FB粉絲團","IG"]
     },
     yAxis: {},
     series: [{
         name: '文章數量',
         type: 'bar',
         data: [{{ FBLenMax }}, {{ FBfanclubLenMax }}, {{ IGLenMax }}],
         itemStyle: {
             color: function(params) {
                 // 根据不同的数据值返回不同的颜色
                 var colorList = ['#c23531', '#2f4554', '#61a0a8'];
                 return colorList[params.dataIndex];
             }
         }
     }]
 };

 // 使用刚指定的配置项和数据显示图表。
 myChart.setOption(option);