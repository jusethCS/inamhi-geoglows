export function translateFrecuency(frecuency: string): string {
  switch (frecuency.toLowerCase()) {
    case "diaria":
      return "daily";
    case "mensual":
      return "monthly";
    case "anual":
      return "annual";
    default:
      return "NA";
  }
}


export function generateDates(startDate: Date, endDate: Date, frequency: string): string[] {
  let generatedDates: string[] = [];
  let currentDate: Date = new Date(startDate);

  // Iterate while the current date is less than or equal to the end date
  while (currentDate <= endDate) {
    // Format the current date as "YYYY-MM-DD"
    let formattedDate: string = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${currentDate.getDate().toString().padStart(2, '0')}`;
    generatedDates.push(formattedDate);

    // Increment the date based on the specified frequency
    switch (frequency.toLowerCase()) {
      case "daily":
        currentDate.setDate(currentDate.getDate() + 1);
        break;
      case "monthly":
        currentDate.setMonth(currentDate.getMonth() + 1);
        break;
      case "annual":
        currentDate.setFullYear(currentDate.getFullYear() + 1);
        break;
      default:
        throw new Error("Invalid frequency");
    }
  }

  return generatedDates;
}


export function convertToCSV(objArray: any[], headers: string[]): string {
  const array = typeof objArray !== 'object' ? JSON.parse(objArray) : objArray;
  let str = '';
  // Get headers
  //const header = Object.keys(array[0]).join(',') + '\r\n';
  //str += header;
  // Use custom headers if provided, otherwise generate from the first object
  const headerLine = headers.length > 0 ? headers.join(',') + '\r\n' : Object.keys(array[0]).join(',') + '\r\n';
  str += headerLine;
  // Get rows
  array.forEach((obj: { [s: string]: unknown; } | ArrayLike<unknown>) => {
    const line = Object.values(obj).join(',') + '\r\n';
    str += line;
  });
  return str;
}


export function downloadFile(data: string, filename: string) {
  const blob = new Blob([data], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.setAttribute('href', url);
  a.setAttribute('download', filename);
  a.click();
  window.URL.revokeObjectURL(url);
}

export function generateDatesGOES1(): string[] {
  const timestamps: string[] = [];
  const now = new Date();
  // Ajustar los minutos al múltiplo de 10 más cercano hacia abajo
  now.setMinutes(Math.floor(now.getMinutes() / 10) * 10);
  now.setSeconds(0);
  now.setMilliseconds(0);
  for (let i = 0; i < 18; i++) {
      const timestamp = now.toISOString().replace(/[-:T]/g, '').substring(0, 12);
      timestamps.push(timestamp);
      now.setMinutes(now.getMinutes() - 10);
  }
  return timestamps.reverse().slice(0, -2);
}

export function generateDatesGOES2(): string[] {
  const timestamps: string[] = [];
  const now = new Date();
  // Ajustar los minutos al múltiplo de 10 más cercano hacia abajo
  now.setMinutes(Math.floor(now.getMinutes() / 10) * 10);
  now.setSeconds(0);
  now.setMilliseconds(0);
  for (let i = 0; i < 18; i++) {
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0'); // Los meses empiezan desde 0
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const timestamp = `${year}-${month}-${day} ${hours}:${minutes}`;
      timestamps.push(timestamp);
      now.setMinutes(now.getMinutes() - 10);
  }
  return timestamps.reverse().slice(0, -2);
}

