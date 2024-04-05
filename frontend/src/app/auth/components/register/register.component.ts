import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';
import {MatButtonModule} from '@angular/material/button';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {FormControl, Validators, FormsModule, ReactiveFormsModule} from '@angular/forms';
import { AuthService } from '../../services/auth.service';


@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    MatInputModule,
    MatIconModule,
    MatButtonModule,
    FormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})


export class RegisterComponent {

  // Form variables and error messages
  email = new FormControl('', [Validators.required, Validators.email]);
  password = new FormControl('', [Validators.required]);
  firstname = new FormControl('', [Validators.required]);
  lastname = new FormControl('', [Validators.required]);
  institution = new FormControl('', [Validators.required]);
  position = new FormControl('', [Validators.required]);

  errorMessageEmail = '';

  // State varible to hide or show password
  hide = true;


  // -------------------------------------------------------------------- //
  //          CONSTRUCTOR: Validate the state of form variables           //
  // -------------------------------------------------------------------- //
  constructor(private router: Router, private authService: AuthService) {
    this.email.valueChanges
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.updateErrorMessageEmail());
  }


  // -------------------------------------------------------------------- //
  //           METHOD: Update status and erros in form values             //
  // -------------------------------------------------------------------- //
  updateErrorMessageEmail() {
    this.errorMessageEmail = this.email.hasError('required')
      ? 'Debe ingresar un correo'
      : this.email.hasError('email')
        ? 'Correo no válido'
        : '';
  }

  // -------------------------------------------------------------------- //
  //          METHOD: Show the login form (user authentication)           //
  // -------------------------------------------------------------------- //
  redirectToLogin() {
    this.router.navigateByUrl('/');
  }

  // -------------------------------------------------------------------- //
  //               METHOD: Register new user into database                //
  // -------------------------------------------------------------------- //
  register(): void{
    const data =  {
      email: this.email.value,
      pass: this.password.value,
      firstname: this.firstname.value,
      lastname: this.lastname.value,
      institution: this.institution.value,
      position: this.position.value
    }
    this.authService.register_user(data).subscribe({
      next: (response) => {
        if (response.status == "success") {
          alert("Usuario ingresado correctamente.")
          this.router.navigateByUrl('/');
        }else{
          alert("No se pudo registrar al usuario. Intente de nuevo.")
        }
      },
      error: (err) => {
        alert("El servidor no pudo procesar su solicitud.")
      }
    })
  }
}
