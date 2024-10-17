import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ImageService {

  constructor() { }

  /**
   * Fetches an image from the provided URL and converts it to a base64 string.
   * @param url - The URL of the image to fetch.
   * @returns A Promise that resolves to the base64 string of the image.
   */
  fetchImageAsBase64(url: string): Promise<string> {
    return fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.blob();
      })
      .then(blob => {
        return new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64data = reader.result as string;
            resolve(base64data); // Return the base64 string
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob); // Convert Blob to base64
        });
      })
      .catch(error => {
        console.error('Error fetching the image:', error);
        throw error;
      });
  }
}
