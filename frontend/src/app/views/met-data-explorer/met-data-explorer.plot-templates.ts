export function pacum_plot(dates:string[], values:string[]){
  let out = {
    data: [{ x: dates, y: values, type: 'bar'}],
    layout: {
      title: "Hietograma",
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



export function temp_plot(dates:string[], values:string[]){
  let out = {
    data: [{ x: dates, y: values, type: 'scatter', mode: 'lines'}],
    layout: { autosize: true, xaxis: { title: ''}, yaxis: { title: 'Temperatura (°C)'} }
  }
  return(out)
}




export function goes_temp_plot(dates:string[], values:string[]){
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

export function goes_gray_plot(dates:string[], values:string[]){
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
