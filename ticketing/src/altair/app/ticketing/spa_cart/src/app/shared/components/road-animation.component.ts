import { Component, OnInit , Input, EventEmitter} from '@angular/core';
//service
import { AnimationEnableService } from '../../shared/services/animation-enable.service';

@Component({
  selector: 'app-road-animation',
  templateUrl: './road-animation.component.html',
  styleUrls: ['./road-animation.component.css']
})
export class RoadAnimationComponent {

  constructor(private animationEnableService: AnimationEnableService) {
  }

  roadAnimeDisplay: boolean;

  ngOnInit() {
    this.animationEnableService.toRoadingFlag$.subscribe(
      flag => {
        this.roadAnimeDisplay = flag;
      });
  }

}