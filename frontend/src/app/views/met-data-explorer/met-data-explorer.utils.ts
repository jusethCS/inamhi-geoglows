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
