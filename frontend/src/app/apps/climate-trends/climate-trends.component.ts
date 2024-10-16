import { Component } from '@angular/core';
import { AppTemplateComponent } from "../../components/template/app-template.component";

@Component({
  selector: 'app-climate-trends',
  standalone: true,
  imports: [AppTemplateComponent],
  templateUrl: './climate-trends.component.html',
  styleUrl: './climate-trends.component.css'
})
export class ClimateTrendsComponent {

}
