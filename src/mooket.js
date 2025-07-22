class mooket {
  constructor(database){
    this.database = database
    this.setupUI();
  }

  setupUI(){
    let self = this;
    self.queryBtn = document.getElementById("datago");
    self.queryString = document.getElementById("query");
    // Connect to the database
    console.log("hi > connect?", self.database);
    self.queryBtn.addEventListener("click",x=>self.plotify(self))
  }

  async plotify(self){
    self.queryString = document.getElementById("query");
    const result = self.database.db.exec( self.queryString.value );
    result.then(data=>{self.doplot(self,data[0])});
  }

  doplot(self, data){
    console.log(data);
    let traces = [];
    let traceDict = {};
    let labels = data.columns;
    for( let index=0; index< labels.length; index++ ){
      traceDict[labels[index]] = [];
      for( let num=0; num < data.values.length; num++ ){
        traceDict[labels[index]].push( data.values[num][index] );
      }
    }
    for( const [key, value] of Object.entries(traceDict) ){
      if( key == 'time' ) continue;
      let trace = {
        name: key,
        x: traceDict['time'],
        y: value,
        type: 'scatter'
      }
      traces.push(trace);
    }
    self.plotlyData = traces;
    let layout = {
      plot_bgcolor: "rgb(66 66 66 / 66%)",
      paper_bgcolor: "rgb(66 66 66 / 66%)",
      font: {color: "#fff",},
      showlegend:true,
    }
    Plotly.newPlot('plot', traces, layout, {responsive:true});
  }
}
