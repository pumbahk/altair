package model;

class Seat extends ElementL1 {
    public function new (tbl:Hash<ElementL1>, id:String, included:Array<String>, memorize_rels:Bool = true) {
        super(tbl, id, included, memorize_rels);
    }
}