export function parseGOESDatetime(dates: string[]): string[] {
  return dates.map(date => {
      // Extract year, month, day, hours, and minutes from the input string
      const [year, month, day, hours, minutes] = [
          parseInt(date.slice(0, 4), 10),     // Year: first 4 characters
          parseInt(date.slice(4, 6), 10) - 1, // Month: subtract 1 as JS months are 0-indexed
          parseInt(date.slice(6, 8), 10),     // Day
          parseInt(date.slice(8, 10), 10),    // Hours
          parseInt(date.slice(10, 12), 10)    // Minutes
      ];

      // Create the date in UTC using the extracted components
      const utcDate = new Date(Date.UTC(year, month, day, hours, minutes));

      // Adjust the date: add 10 minutes and subtract 5 hours
      utcDate.setUTCMinutes(utcDate.getUTCMinutes() + 10);
      utcDate.setUTCHours(utcDate.getUTCHours() - 5);

      // Get the adjusted local date components and format them
      const localDateComponents = {
          year: utcDate.getUTCFullYear(),                     // Get full year
          month: String(utcDate.getUTCMonth() + 1).padStart(2, '0'), // Adjust month (0-indexed) and format
          day: String(utcDate.getUTCDate()).padStart(2, '0'),         // Format day
          hours: String(utcDate.getUTCHours()).padStart(2, '0'),      // Format hours
          minutes: String(utcDate.getUTCMinutes()).padStart(2, '0')   // Format minutes
      };

      // Return the formatted date string in 'YYYY-MM-DD HH:MM' format
      return `${localDateComponents.year}-${localDateComponents.month}-${localDateComponents.day} ${localDateComponents.hours}:${localDateComponents.minutes}`;
  });
}

