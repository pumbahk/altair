import { Injectable } from '@angular/core';
// interfaces
import { IProducts, IProductItems } from './interfaces';

@Injectable()
export class QuantityCheckService {
  /**
* 席種単位での購入上限枚数チェック
*
* @param  {number} upper_limit - 販売区分の購入上限枚数:salesSagment.upper_limit
* @param  {number} max_quantity - 席種毎の最大購入枚数:stockType.max_quantity
* @param  {number} quantity - 枚数
* @return {boolean}
*/
  stockTypeQuantityMaxLimitCheck(upper_limit: number, max_quantity: number, quantity: number) {
    //両方ある場合は設定枚数の少ない方で
    //どちらもない場合はチェックなし
    if (upper_limit && max_quantity) {
      if (upper_limit < max_quantity) {
        if (upper_limit < quantity) {
          return false;
        }
      } else {
        if (max_quantity < quantity) {
          return false;
        }
      }
    } else if (upper_limit) {
      if (upper_limit < quantity) {
        return false;
      }
    } else if (max_quantity) {
      if (max_quantity < quantity) {
        return false;
      }
    }
    return true;
  }
  /**
* 席種単位での購入下限枚数チェック
*
* @param  {number} min_quantity - 席種毎の最小購入枚数:stockType.min_quantity
* @param  {number} quantity - 枚数
* @return {boolean}
*/
  stockTypeQuantityMinLimitCheck(min_quantity: number, quantity: number) {
    //席種毎の最小購入枚数が無い場合はデフォルト１でチェック
    const DEFAULT_MIN_NUMBER = 1;
    if (min_quantity) {
      if (min_quantity > quantity) {
        return false;
      }
    } else {
      if (DEFAULT_MIN_NUMBER > quantity) {
        return false;
      }
    }
    return true;
  }

  /**
* 席種単位での商品上限個数チェック
* @param  {number} upper_limit - 販売区分の購入上限枚数:salesSagment.upper_limit
* @param  {number} max_product_quantity - 席種毎の最大購入数:stockType.max_product_quantity
* @param  {number} product_quantity - 選択した商品数
* @return {boolean}
*/
  stockTypeProductMaxLimitCheck(upper_limit: number, max_product_quantity: number, product_quantity: number) {
    //両方ある場合は設定枚数の少ない方で
    //どちらもない場合はチェックなし
    if (upper_limit && max_product_quantity) {
      if (upper_limit < max_product_quantity) {
        if (upper_limit < product_quantity) {
          return true;
        }
      } else {
        if (max_product_quantity < product_quantity) {
          return true;
        }
      }
    } else if (upper_limit) {
      if (upper_limit < product_quantity) {
        return true;
      }
    } else if (max_product_quantity) {
      if (max_product_quantity < product_quantity) {
        return true;
      }
    }
    return false;
  }

  /**
* 席種単位での商品下限個数チェック
* @param  {number} min_product_quantity - 席種毎の最大購入数:stockType.min_product_quantity
* @param  {number} product_quantity - 選択した商品数
* @return {boolean}
*/
  stockTypeProductMinLimitCheck(min_product_quantity: number, product_quantity: number) {
    //設定がない場合はチェックなし。
    if (min_product_quantity) {
      if (min_product_quantity > product_quantity) {
        return true;
      }
    }
    return false;
  }

  /**
* 商品単位での商品上限個数チェック+残席数に対する販売単位のチェックを行います
* @param  {number} max_product_quantity - 商品の商品購入上限数:Product.max_product_quantity
* @param  {number} sales_unit_quantity - 販売単位
* @param  {number} selected_quantity - 選択座席数
* @param  {number} un_selected_quantity - 未選択座席数
* @return {boolean}
*/
  productMaxLimitCheck(max_product_quantity: number, sales_unit_quantity: number, selected_quantity: number, un_selected_quantity: number) {
    let max_purchase_possible_quantity = null;
    //残席数に対する販売単位のチェック
    if (un_selected_quantity < sales_unit_quantity) {
      return true
    }
    //設定が無い場合はチェックなし
    if (max_product_quantity) {
      //最大購入可能枚数を求める
      max_purchase_possible_quantity = max_product_quantity * sales_unit_quantity;
      if (max_purchase_possible_quantity <= selected_quantity) {
        return true;
      }
    }
    return false;
  }

  /**
* 商品単位での商品下限個数チェック
* @param  {number} min_product_quantity - 商品の商品購入下限数:Product.min_product_quantity
* @param  {number} selected_quantity - 選択座席数
* @return {boolean}
*/
  productMinLimitCheck(min_product_quantity: number, selected_quantity: number) {
    //設定が無い場合はチェックなし
    if (min_product_quantity) {
      if (min_product_quantity > selected_quantity) {
        return true
      }
    }
    return false;
  }

  /**
* 必須選択商品チェック
* @param  {boolean}  must_be_chosen - 必須選択
* @param  {number}   selected_quantity - 選択座席数
* @return {boolean}
*/
  mustBeChosenCheck(must_be_chosen: boolean, selected_quantity: number) {
    if (must_be_chosen && !selected_quantity) {
      return true;
    }
    return false
  }

  /**
* 販売単位チェック
* 席種の中でその選択席数がその販売単位の倍数ではない場合、エラーとする。
* @param  {IProducts[]} products - 商品情報
* @param  {number} quantity - 選択座席数
* @return {number}
*/
  salesUnitCheck(products: IProducts[], quantity: number) {
    let salesUnitNumber: number = null;
    let result: number = null;
    for (let i = 0, len = products.length; i < len; i++) {
      salesUnitNumber = null;
      for (let j = 0, len = products[i].product_items.length; j < len; j++) {
        if (products[i].product_items[j].sales_unit_quantity) {
          salesUnitNumber += products[i].product_items[j].sales_unit_quantity;
        }
      }
      if ((quantity % salesUnitNumber) == 0) {
        return null;
      } else {
        result = salesUnitNumber;
      }
    }
    return result;
  }

  /**
* 枚数選択表示用配列作成、販売単位1を削除する関数
* @param  {IProducts[]} products - 商品情報
* @return {number[]}
*/
  eraseOne(products: IProducts[]) {
    const ERASE_NUMBER: number = 1;
    let result: number[] = [];
    for (let i = 0, len = products.length; i < len; i++) {
      let sum: number = null;
      for (let j = 0, len = products[i].product_items.length; j < len; j++) {
        if (products[i].product_items.length == 1 && products[i].product_items[0].sales_unit_quantity == ERASE_NUMBER) {
          result.push(null);
          break;
        } else {
          sum += products[i].product_items[j].sales_unit_quantity;
        }
      }
      if (sum) {
        result.push(sum);
      }
    }
    return result;
  }

  /**
* 残席数に対する販売単位のチェックを行います

* @param  {number} selected_quantity - 選択座席数
* @return {boolean}
*/
  selectedQuantityMinLimitCheck(selected_quantity: number) {
    const FALSE_NUMBER: number = 1;
    //残席数に対する販売単位のチェック
    if (FALSE_NUMBER > selected_quantity) {
      return true
    }
    return false;
  }

  /**
* 未割当枚数チェック
* @param  {number}  num - 未割当枚数
* @return {boolean}
*/
  unassignedSeatCheck(num: number) {
    if (num > 0) {
      return true;
    }
    return false
  }
}