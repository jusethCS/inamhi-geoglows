import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { ImageService } from '../../services/image.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-image',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './image.component.html',
  styleUrl: './image.component.css'
})

export class ImageComponent {
  @Input() imageUrl: string | undefined;
  public base64Image: string | undefined;

  constructor(private imageService: ImageService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['imageUrl'] && this.imageUrl) {
      this.loadImage(this.imageUrl);
    }
  }

  public loadImage(url: string): void {
    this.imageService.fetchImageAsBase64(url)
      .then(base64 => {
        this.base64Image = base64;
      })
      .catch(error => console.error('Error loading image:', error));
  }
}
