import { Component, OnInit, AfterViewInit } from '@angular/core';
//interfaces
import { IPerformance, IPerformanceInfoResponse } from '../shared/services/interfaces';
//router
import {
    ActivatedRoute,
    Router,
    // import as RouterEvent to avoid confusion with the DOM Event
    Event as RouterEvent,
    NavigationStart,
    NavigationEnd,
    NavigationCancel,
    NavigationError
} from '@angular/router';
//services
import { LoadingAnimateService } from 'ng2-loading-animate';
//jquery
import * as $ from 'jquery';

@Component({
  selector: 'app-reserve-by-seat',
  templateUrl: './reserve-by-seat.component.html',
  styleUrls: ['./reserve-by-seat.component.css']
})
export class ReserveBySeatComponent implements OnInit {

  //ページタイトル
  pageTitle: string;

  //公演id
  performanceId: number;

  // マップの高さ
  mapAreaLeftH: number = 0;

  // マップの高さ取得フラグ
  isGetMapH: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private loadingService: LoadingAnimateService) {
  }

  ngOnInit() {
    //ローディング表示
    this.loadingService.setValue(true);
    const that = this;

    $(function () {
      var windowWidth = $(window).width();
      var windowSm = 768;
      //filterの初期表示
      if (windowWidth <= windowSm) {
        $(document).ready(function () {
          $('.acdBt').click(function () {
            $(this).next().slideToggle(300);
          }).next().hide();
        })
      }

      function setting() {
        var mainH;
        var windowH;
        var windowWidth = $(window).width();
        var windowSm = 768;
        if (windowWidth <= windowSm) {
          //横幅768px以下のとき（つまりスマホ時）に行う処理を書く
          $(function () {
            function heightSetting() {
              let minus = 0;
              if ($('#modalWindow').length) {
                minus = 149;
              } else if ($('#choiceSeatArea').length) {
                minus = 280;
              } else {
                minus = 149;
              }
              let mainID = 'mapAreaLeft';
              //スマホサイズのPC対応
              if (!($('#modalWindowStockTypeAlertBox').length) && !($('#buyChoiceSeatArea').length)) {
                $('#' + mainID).height(mainH + 'px');
                that.mapAreaLeftH = mainH;
                that.isGetMapH = true;
              }
            }
            heightSetting();
          });
          $(function () {
            var mainID = 'mapAreaRight'
            function heightSetting() {
              $('#' + mainID).height("100%");
            }
            heightSetting();
          });

        } else {
          //横幅768px超のとき（タブレット、PC）に行う処理を書く
          $(function () {
            var minus = 240
            var mainID = 'mapAreaLeft'
            function heightSetting() {
              windowH = $(window).height();
              mainH = windowH - minus;
              $('#' + mainID).height(mainH + 'px');
              that.mapAreaLeftH = mainH;
              that.isGetMapH = true;
            }
            heightSetting();
          });
          $(function () {
            var minus = 220
            var mainID = 'mapAreaRight'
            function heightSetting() {
              windowH = $(window).height();
              mainH = windowH - minus;

              $('#' + mainID).height(mainH + 'px');
            }
            heightSetting();
          });
          $(function () {
            var minus = 169
            var mainID = 'buySeatArea'
            function heightSetting() {
              windowH = $(window).height();
              mainH = windowH - minus;
              $('#' + mainID).height(mainH + 'px');
            }
            heightSetting();
          });
        }
      }
      setting();
      $(window).resize(function () {
        setting();
      });
    });

    /*/////////////////////PC・SP両方/////////////////////////*/


    $(function () {
      //venue-mapの選択した座席リスト、select-productのtoggle
      $("#mapAreaRight").on("click", ".selectBoxBtn", function () {
        $(this).prev().slideToggle(300);
        // activeが存在する場合
        if ($(this).children(".closeBtnBox").hasClass('active')) {
          // activeを削除
          $(this).children(".closeBtnBox").removeClass('active');
        } else {
          // activeを追加
          $(this).children(".closeBtnBox").addClass('active');
        }
      });
    });

    //seat-listのボタンのtoggle
    $(function () {
      $(".acd dd").css("display", "none");
      $("#mapAreaRight").on("click", ".acd dt", function () {
        if ($(this).children().attr('class') != "close") {
          $(this).next("dd").slideToggle();
          $(this).next("dd").parent().siblings().find("dd").slideUp();
          $(this).toggleClass("open");
          $(this).parent().siblings().find("dt").removeClass("open");
        }
      });
    });
  }

  ngAfterViewInit(): void {
    //ローディング非表示
    this.loadingService.setValue(false);
  }
}
