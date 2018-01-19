import { Injectable } from '@angular/core';
// interfaces
import { IProducts, IProductItems } from './interfaces';

@Injectable()
export class QuentityCheckService{
    private defaultMaxQuantity:number = 14;
    private defaultMinQuantity:number = 1;

    /**
   * 購入上限枚数チェックを行います
   *
   * @param  {number} maxQuantity - 最大購入数
   * @param  {number} performanceOrderLimit - 購入上限枚数:perormance.order-limit
   * @param  {number} eventOrderLimit - 購入上限枚数:event.order-limit
   * @param  {number} quantity - 枚数
   * @return {boolean}
   */
    maxLimitCheck(maxQuantity:number,performanceOrderLimit:number,eventOrderLimit:number,quantity:number){
        if(maxQuantity){
            if(quantity > maxQuantity){
                return false;
            }
        }else{
            if(performanceOrderLimit){
                if(quantity > performanceOrderLimit){
                    return false;
                }
            }else{
                if(eventOrderLimit){
                    if(quantity > eventOrderLimit){
                        return false;
                    }
                }else{
                    if(quantity > this.defaultMaxQuantity){
                        return false;
                    }
                }
            }
        }
        return true;
    }

     /**
   * 購入下限枚数チェックを行います
   *
   * @param  {number} minQuantity - 最小購入数
   * @param  {number} quantity - 枚数
   * @return {boolean}
   */
    minLimitCheck(minQuantity:number,quantity:number){
        if(minQuantity){
            if(quantity < minQuantity){
                return false;
            }
        }else{
            if(quantity < this.defaultMinQuantity){
                return false;
            }
        }
        return true;
    }

     /**
   * 販売単位のチェックを行います
   * 席種の中でその選択席数がその販売単位の倍数ではない場合、エラーとする。
   * @param  {IProducts[]} products - 商品情報
   * @param  {number} quantity - 選択座席数
   * @return {number}
   */
    salesUnitCheck(products:IProducts[],quantity:number){
        const FALSE_NUMBER:number = 1;
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
    eraseOne(products:IProducts[]){
        const ERASE_NUMBER:number = 1;
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
}