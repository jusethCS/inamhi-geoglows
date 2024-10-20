export function formatDates(date: Date): string[] {
  const months = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
  ];
  const day = date.getDate();
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const format1 = `${day} de ${month} del ${year}, ${hours}:${minutes}`;
  date.setDate(date.getDate() + 1);
  const startDay = date.getDate();
  const startMonth = months[date.getMonth()];
  const startYear = date.getFullYear();
  const endDate = new Date(date);
  endDate.setDate(date.getDate() + 1);
  const endDay = endDate.getDate();
  const endMonth = months[endDate.getMonth()];
  const endYear = endDate.getFullYear();
  const format2 = `desde las 07:00 del ${startDay} de ${startMonth} hasta las 07:00 del ${endDay} de ${endMonth} del ${endYear}`;
  const format3 = `desde el ${startDay} de ${startMonth} del ${startYear} (07H00) hasta el ${endDay} de ${endMonth} del ${endYear} (07H00)`;
  return [format1, format2, format3];
}


export function formatDatesWeekly(date: Date): string[] {
  const months = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
  ];
  const day = date.getDate();
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const format1 = `${day} de ${month} del ${year}, ${hours}:${minutes}`;
  date.setDate(date.getDate() + 1);
  const startDay = date.getDate();
  const startMonth = months[date.getMonth()];
  const startYear = date.getFullYear();
  const endDate = new Date(date);
  endDate.setDate(date.getDate() + 7);
  const endDay = endDate.getDate();
  const endMonth = months[endDate.getMonth()];
  const endYear = endDate.getFullYear();
  const format2 = `desde las 07:00 del ${startDay} de ${startMonth} hasta las 07:00 del ${endDay} de ${endMonth} del ${endYear}`;
  const format3 = `desde el ${startDay} de ${startMonth} del ${startYear} (07H00) hasta el ${endDay} de ${endMonth} del ${endYear} (07H00)`;
  return [format1, format2, format3];
}


export function buildUrl(baseUrl: string, params: Record<string, any>): string {
  // Create a query string by encoding each parameter key and value
  const queryString = Object.keys(params)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');

  // Return the complete URL with the query string appended
  return `${baseUrl}?${queryString}`;
}
