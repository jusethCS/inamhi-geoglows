interface GeoJSONFeature {
  id: string;
  type: string;
  properties: {
    latitude: number;
    longitude: number;
    datetime: string;
    step: number;
  };
  geometry: {
    type: string;
    coordinates: [number, number];
  };
  bbox: [number, number, number, number];
}

interface GeoJSON {
  type: string;
  features: GeoJSONFeature[];
  bbox: [number, number, number, number];
}

export class utils{

  public generateSatelliteDates(startDate: Date, endDate: Date, frequency: string, layer:boolean): string[] {
    let generatedDates: string[] = [];
    let currentDate: Date = new Date(startDate);

    while (currentDate <= endDate) {
        if (frequency.toLowerCase() === 'horaria') {
            let currentHour: Date = new Date(currentDate);
            currentHour.setHours(0);
            currentHour.setMinutes(0);
            currentHour.setSeconds(0);
            currentHour.setMilliseconds(0);
            endDate.setHours(23);
            endDate.setMinutes(59);

            while (currentHour <= endDate && currentHour.getDate() === currentDate.getDate()) {
                let formattedDate: string = `${currentHour.getFullYear()}-${(currentHour.getMonth() + 1).toString().padStart(2, '0')}-${currentHour.getDate().toString().padStart(2, '0')} ${currentHour.getHours().toString().padStart(2, '0')}:${currentHour.getMinutes().toString().padStart(2, '0')}`;
                if(layer){
                  formattedDate = `${currentHour.getFullYear()}-${(currentHour.getMonth() + 1).toString().padStart(2, '0')}-${currentHour.getDate().toString().padStart(2, '0')}T${currentHour.getHours().toString().padStart(2, '0')}${currentHour.getMinutes().toString().padStart(2, '0')}`;
                }
                generatedDates.push(formattedDate);
                currentHour.setHours(currentHour.getHours() + 1);
            }
            currentDate.setDate(currentDate.getDate() + 1);
        } else {
            let formattedDate: string = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${currentDate.getDate().toString().padStart(2, '0')}`;
            generatedDates.push(formattedDate);

            switch (frequency.toLowerCase()) {
                case 'diaria':
                    currentDate.setDate(currentDate.getDate() + 1);
                    break;
                case 'mensual':
                    currentDate.setMonth(currentDate.getMonth() + 1);
                    break;
                case 'anual':
                    currentDate.setFullYear(currentDate.getFullYear() + 1);
                    break;
                default:
                    throw new Error('Invalid frequency');
            }
        }
    }

    return generatedDates;
  }


  public async getLastLayers(wmsUrl: string, lastLayerNumber: number): Promise<string[]> {
    try {
        const response = await fetch(wmsUrl);
        const text = await response.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(text, "application/xml");
        const layers = xmlDoc.getElementsByTagName("Layer");
        const layerList: string[] = [];
        for (let i = 0; i < layers.length; i++) {
            const layerNameElement = layers[i].getElementsByTagName("Name")[0];
            if (layerNameElement && layerNameElement.textContent) {
                layerList.push(layerNameElement.textContent);
            }
        }
        return layerList.slice(-lastLayerNumber);
    } catch (error) {
        console.error('Error al solicitar GetCapabilities:', error);
        return [];
    }
  }


  public parseGOESDate(dates: string[]): string[] {
    return dates.map(date => {
        const year = parseInt(date.slice(0, 4), 10);
        const month = parseInt(date.slice(4, 6), 10) - 1;
        const day = parseInt(date.slice(6, 8), 10);
        const hours = parseInt(date.slice(8, 10), 10);
        const minutes = parseInt(date.slice(10, 12), 10);
        const utcDate = new Date(Date.UTC(year, month, day, hours, minutes));
        utcDate.setUTCMinutes(utcDate.getUTCMinutes() + 10);
        utcDate.setUTCHours(utcDate.getUTCHours() - 5);
        const localYear = utcDate.getUTCFullYear();
        const localMonth = String(utcDate.getUTCMonth() + 1).padStart(2, '0');
        const localDay = String(utcDate.getUTCDate()).padStart(2, '0');
        const localHours = String(utcDate.getUTCHours()).padStart(2, '0');
        const localMinutes = String(utcDate.getUTCMinutes()).padStart(2, '0');
        return `${localYear}-${localMonth}-${localDay} ${localHours}:${localMinutes}`;
    });
}


  public async getLayersStartWidth(wmsUrl: string, query:string): Promise<string[]> {
    try {
      const response = await fetch(`${wmsUrl}?service=WMS&request=GetCapabilities`);
      const text = await response.text();
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(text, "application/xml");
      const layers = xmlDoc.getElementsByTagName("Layer");
      const layerList: string[] = [];
      for (let i = 0; i < layers.length; i++) {
          const layerNameElement = layers[i].getElementsByTagName("Name")[0];
          if (layerNameElement &&
              layerNameElement.textContent &&
              layerNameElement.textContent.startsWith(query)) {
                layerList.push(layerNameElement.textContent);
          }
      }
      return Array.from(new Set(layerList));
    } catch (error) {
      console.error('Error al solicitar GetCapabilities:', error);
      return [];
    }
  }



  public getInitForecastDate(today:boolean = true): string {
    const now = new Date();
    if(!today){
      now.setUTCDate(now.getUTCDate() - 1)
    }
    const year = now.getUTCFullYear();
    const month = String(now.getUTCMonth() + 1).padStart(2, '0');
    const day = String(now.getUTCDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  public getAcumulatedDate7():string{
    let today = new Date();
    if (today.getHours() < 8) {
      today.setDate(today.getDate() - 1);
    }
    const year_today = today.getUTCFullYear();
    const month_today = String(today.getUTCMonth() + 1).padStart(2, '0');
    const day_today = String(today.getUTCDate()).padStart(2, '0');

    let yesterday = new Date(today);
    yesterday.setUTCDate(today.getUTCDate() - 1);
    const year_yesterday = yesterday.getUTCFullYear();
    const month_yesterday = String(yesterday.getUTCMonth() + 1).padStart(2, '0');
    const day_yesterday = String(yesterday.getUTCDate()).padStart(2, '0');

    return `<b>Desde</b> ${year_yesterday}-${month_yesterday}-${day_yesterday} 07:00 <b>hasta</b> ${year_today}-${month_today}-${day_today} 07:00`
  }

  public getAcumulatedDate48():string{
    let today = new Date();
    if (today.getHours() < 8) {
      today.setDate(today.getDate() - 1);
    }
    const year_today = today.getUTCFullYear();
    const month_today = String(today.getUTCMonth() + 1).padStart(2, '0');
    const day_today = String(today.getUTCDate()).padStart(2, '0');

    let yesterday = new Date(today);
    yesterday.setUTCDate(today.getUTCDate() - 2);
    const year_yesterday = yesterday.getUTCFullYear();
    const month_yesterday = String(yesterday.getUTCMonth() + 1).padStart(2, '0');
    const day_yesterday = String(yesterday.getUTCDate()).padStart(2, '0');

    return `<b>Desde</b> ${year_yesterday}-${month_yesterday}-${day_yesterday} 07:00 <b>hasta</b> ${year_today}-${month_today}-${day_today} 07:00`
  }

  public getAcumulatedDate72():string{
    let today = new Date();
    if (today.getHours() < 8) {
      today.setDate(today.getDate() - 1);
    }
    const year_today = today.getUTCFullYear();
    const month_today = String(today.getUTCMonth() + 1).padStart(2, '0');
    const day_today = String(today.getUTCDate()).padStart(2, '0');

    let yesterday = new Date(today);
    yesterday.setUTCDate(today.getUTCDate() - 3);
    const year_yesterday = yesterday.getUTCFullYear();
    const month_yesterday = String(yesterday.getUTCMonth() + 1).padStart(2, '0');
    const day_yesterday = String(yesterday.getUTCDate()).padStart(2, '0');

    return `<b>Desde</b> ${year_yesterday}-${month_yesterday}-${day_yesterday} 07:00 <b>hasta</b> ${year_today}-${month_today}-${day_today} 07:00`
  }


  public getFFGSDate():string{
    let today = new Date();
    const year_today = today.getFullYear();
    const month_today = String(today.getMonth() + 1).padStart(2, '0');
    const day_today = String(today.getDate()).padStart(2, '0');
    const hour_today = String(today.getHours()).padStart(2, '0');
    return `${year_today}-${month_today}-${day_today} ${hour_today}:00`
  }

  public getUpdateNoRain():string{
    let today = new Date();
    if (today.getHours() < 8) {
      today.setDate(today.getDate() - 1);
    }
    const year_today = today.getUTCFullYear();
    const month_today = String(today.getUTCMonth() + 1).padStart(2, '0');
    const day_today = String(today.getUTCDate()).padStart(2, '0');

    return `<b>Última actualización:</b> ${year_today}-${month_today}-${day_today} 07:00<br><span style='font-size:10px; font-weigth:200'>*Se considera "sin lluvia significativa" a días con precipitaciones acumuladas menores a 2mm</span>`
  }

  public formatForecastDate(input: string): string {
    let regex = /(\d{4}-\d{2}-\d{2})(\d{2}Z)-(\d+H)-(\d{8})(\d{2}h\d{2})/;
    let matches = input.match(regex);
    if (!matches) {
      regex = /(\d{4}-\d{2}-\d{2})(\d{2}Z)-(\d+W)-(\d{8})(\d{2}h\d{2})/;
      matches = input.match(regex);
      if (!matches) {
        throw new Error("El formato del string de entrada no es válido");
      }
    }
    const [_, date, timeZ, duration, forecastDate, forecastTime] = matches;
    const result = `<b>Inicialización:</b> ${date} ${timeZ}. <b>Pronóstico:</b> ${forecastDate.slice(0, 4)}-${forecastDate.slice(4, 6)}-${forecastDate.slice(6, 8)} ${forecastTime.replace('h', ':')}`;
    return result;
  }

  public formatForecastDatePlot(input: string): string {
    let regex = /(\d{4}-\d{2}-\d{2})(\d{2}Z)-(\d+H)-(\d{8})(\d{2}h\d{2})/;
    let matches = input.match(regex);
    if (!matches) {
      regex = /(\d{4}-\d{2}-\d{2})(\d{2}Z)-(\d+W)-(\d{8})(\d{2}h\d{2})/;
      matches = input.match(regex);
      if (!matches) {
        throw new Error("El formato del string de entrada no es válido");
      }
    }
    const [_, date, timeZ, duration, forecastDate, forecastTime] = matches;
    const result = `${forecastDate.slice(0, 4)}-${forecastDate.slice(4, 6)}-${forecastDate.slice(6, 8)} ${forecastTime.replace('h', ':')}:00`;
    return result;
  }

  public buildUrl(baseUrl: string, params: any): string {
    const queryString = Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
    return `${baseUrl}?${queryString}`;
  }



  public filterByDay(geojson: any, propertyKey: string) {
    const aa = {
      type: geojson.type,
      features: geojson.features.map(
        (feature: {
          type: any;
          id: any;
          properties: { [x: string]: any; };
          geometry: any;
          bbox: any;
        }) => ({
          type: feature.type,
          id: feature.id,
          properties: {
            "comid": feature.properties["comid"],
            "latitude": feature.properties["latitude"],
            "longitude": feature.properties["longitude"],
            "river": feature.properties["river"],
            "location1": feature.properties["location1"],
            "location2": feature.properties["location2"],
            "alert": feature.properties[propertyKey]
          },
          geometry: feature.geometry,
          bbox: feature.bbox
      }))
    };
    return aa;
  }


  public filterByDayWaterLevel(geojson: any, propertyKey: string) {
    const aa = {
      type: geojson.type,
      features: geojson.features.map(
        (feature: {
          type: any;
          id: any;
          properties: { [x: string]: any; };
          geometry: any;
          bbox: any;
        }) => ({
          type: feature.type,
          id: feature.id,
          properties: {
            "comid": feature.properties["comid"],
            "code": feature.properties["code"],
            "name": feature.properties["name"],
            "latitude": feature.properties["latitude"],
            "longitude": feature.properties["longitude"],
            "river": feature.properties["river"],
            "location1": feature.properties["location1"],
            "location2": feature.properties["location2"],
            "alert": feature.properties[propertyKey]
          },
          geometry: feature.geometry,
          bbox: feature.bbox
      }))
    };
    return aa;
  }


  public filterByRP(geojson:any, condition:string){
    const aa = geojson;
    const filtered = {
      type: aa.type,
      features: aa.features.filter(
        (feature: {
          type: any;
          id: any;
          properties: { [x: string]: any; };
          geometry: any;
          bbox: any;
        }) => feature.properties["alert"] === condition
      )
    };
    return filtered;
  }

  public getDateRangeGeoglows(selectedDate: Date): string[] {
    const result: string[] = [];
    const startDate = new Date(selectedDate);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 14);
    let currentDate = startDate;
    while (currentDate <= endDate) {
      const year = currentDate.getFullYear();
      const month = String(currentDate.getMonth() + 1).padStart(2, '0');
      const day = String(currentDate.getDate()).padStart(2, '0');
      result.push(`${year}-${month}-${day}`);
      currentDate.setDate(currentDate.getDate() + 1);
    }
    return result;
  }


  public filterHotSpots(geojson: GeoJSON): GeoJSON[] {
    const maxStep = Math.max(...geojson.features.map(feature => feature.properties.step));
    const filteredGeoJSONs: GeoJSON[] = [];

    for (let step = 0; step <= maxStep; step++) {
      const filteredFeatures = geojson.features.filter(feature => feature.properties.step === step);

      filteredGeoJSONs.push({
        ...geojson,
        features: filteredFeatures
      });
    }
    return filteredGeoJSONs;
  }

  public formatDateForecast(type: string, input: string): string {
    let regex = /(\d{4}-\d{2}-\d{2})(\d{2}Z)-(\d+H)-(\d{8})(\d{2}h\d{2})/;
    let matches = input.match(regex);
    if (!matches) {
      regex = /(\d{4}-\d{2}-\d{2})(\d{2}Z)-(\d+W)-(\d{8})(\d{2}h\d{2})/;
      matches = input.match(regex);
      if (!matches) {
        throw new Error("El formato del string de entrada no es válido");
      }
    }

    const [_, date, timeZ, duration, forecastDate, forecastTime] = matches;

    let forecastDateTimeInit = new Date(`${forecastDate.slice(0, 4)}-${forecastDate.slice(4, 6)}-${forecastDate.slice(6, 8)}T${forecastTime.replace('h', ':')}:00Z`);
    let forecastDateTimeEnd = new Date(`${forecastDate.slice(0, 4)}-${forecastDate.slice(4, 6)}-${forecastDate.slice(6, 8)}T${forecastTime.replace('h', ':')}:00Z`);

    if (type === "3H") {
        forecastDateTimeEnd.setHours(forecastDateTimeEnd.getHours() + 3);
    } else if (type === "24H") {
        forecastDateTimeEnd.setHours(forecastDateTimeEnd.getHours() + 24);
    } else if (type === "1W") {
        forecastDateTimeEnd.setDate(forecastDateTimeEnd.getDate() + 7);
    }

    // Formatear la nueva fecha y hora
    const dateInit = forecastDateTimeInit.toISOString().slice(0, 10);
    const timeInit = forecastDateTimeInit.toISOString().slice(11, 16);
    const dateEnd = forecastDateTimeEnd.toISOString().slice(0, 10);
    const timeEnd = forecastDateTimeEnd.toISOString().slice(11, 16);

    const result = `
      <b>Inicialización:</b> ${date} ${timeZ}. <br>
      <b>Desde</b> ${dateInit} ${timeInit} <b>Hasta</b> ${dateEnd} ${timeEnd}
    `;
    return result;
}



}



