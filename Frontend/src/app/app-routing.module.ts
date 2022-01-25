import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AppComponent } from './app.component';
import { Routes } from '@angular/router';

const routes: Routes = [
  { path: 'main', component: AppComponent }
];

@NgModule({
  declarations: [],
  imports: [
    CommonModule
  ]
})
export class AppRoutingModule { }
