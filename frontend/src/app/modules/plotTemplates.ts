import { marker } from "leaflet";

export class plotTemplates{

  public pacumPlotTemplate(dates:string[], values:string[]){
    let out = {
      data: [{
        x: dates,
        y: values,
        type: 'bar',
        marker: { color: "#1E9AB9"}
      }],
      layout: {
        title: "Precipitación",
        autosize: true,
        margin: { l: 50, r: 30, b: 40, t: 50 },
        xaxis: {
          title: '',
          linecolor: "black",
          linewidth: 1,
          showgrid: false,
          showline: true,
          mirror: true,
          ticks: "outside",
          automargin: true,
        },
        yaxis: {
          title: 'Precipitación (mm)',
          linecolor: "black",
          linewidth: 1,
          showgrid: false,
          showline: true,
          mirror: true,
          ticks: "outside",
          automargin: true,
        }
      }
    };
    return(out)
  }



  public tempPlotTemplate(dates:string[], values:string[]){
    return(
      {
        data: [{
          x: dates,
          y: values,
          type: 'scatter',
          mode: 'lines',
          line: { color: "#DAA939"}
        }],
        layout: {
          title: "Temperatura del aire",
          autosize: true,
          margin: { l: 50, r: 30, b: 40, t: 50 },
          xaxis: {
            title: '',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          },
          yaxis: {
            title: 'Temperatura (°C)',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          }
        }
      }
    )
  }


  public hrPlotTemplate(dates:string[], values:string[]){
    return(
      {
        data: [{
          x: dates,
          y: values,
          type: 'scatter',
          mode: 'lines',
          line: { color: "#1EB7B9"}
        }],
        layout: {
          title: "Humedad relativa",
          autosize: true,
          margin: { l: 50, r: 30, b: 40, t: 50 },
          xaxis: {
            title: '',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          },
          yaxis: {
            title: 'Humedad relativa (%)',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          }
        }
      }
    )
  }

  public windPlotTemplate(dates:string[], values:string[]){
    return(
      {
        data: [{
          x: dates,
          y: values,
          type: 'scatter',
          mode: 'lines',
          line: { color: "#B9461E"}
        }],
        layout: {
          title: "Velocidad del viento",
          autosize: true,
          margin: { l: 50, r: 30, b: 40, t: 50 },
          xaxis: {
            title: '',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          },
          yaxis: {
            title: 'Velocidad del viento (m/s)',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          }
        }
      }
    )
  }




  public goesTempPlotTemplate(dates:string[], values:string[]){
    return(
      {
        data: [{ x: dates, y: values, type: 'scatter', mode: 'lines'}],
        layout: {
          title: "GOES temperatura de brillo",
          autosize: true,
          margin: { l: 50, r: 30, b: 40, t: 50 },
          xaxis: {
            title: '',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          },
          yaxis: {
            title: 'Temperatura (°K)',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          }
        }
      }
    )
  }

  public goesGrayPlotTemplate(dates:string[], values:string[]){
    return(
      {
        data: [{ x: dates, y: values, type: 'scatter', mode: 'lines'}],
        layout: {
          title: "GOES banda visible",
          autosize: true,
          margin: { l: 50, r: 30, b: 40, t: 50 },
          xaxis: {
            title: '',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          },
          yaxis: {
            title: 'Gray Scale (%)',
            linecolor: "black",
            linewidth: 1,
            showgrid: false,
            showline: true,
            mirror: true,
            ticks: "outside",
            automargin: true,
          }
        }
      }
    )
  }





}

