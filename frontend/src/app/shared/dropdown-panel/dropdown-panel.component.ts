import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MatExpansionModule, MatAccordion } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-dropdown-panel',
  standalone: true,
  imports: [
    CommonModule,
    MatExpansionModule,
    MatAccordion,
    MatFormFieldModule,
    MatIconModule
  ],
  templateUrl: './dropdown-panel.component.html',
  styleUrl: './dropdown-panel.component.css'
})
export class DropdownPanelComponent {

  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //

  @Input() expanded: boolean = false;
  @Input() iconClass: string = "fa-brands fa-angular";
  @Input() title: string = "";


}
