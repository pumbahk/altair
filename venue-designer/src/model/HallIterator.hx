package model;

class HallIterator {

    private var _parents:Array<Element>;
    private var _roots:Array<Element>;

    public function new(hall:HallView) {

        this._parents = [];
        this._roots = [];
        var firsts:Array<Element> = [];

        for (i in hall.roots()) {
            var et:ElementType = i.type();
            if (et == ElementType.plainShape || et == ElementType.unknown) {
                firsts.push(i);
            } else {
                this._roots.push(i);
            }
        }

        this._roots = firsts.concat(this._roots);

/*
        for(i in this._roots) {
            Console.log(i);
        }
*/
    }

    public function hasNext():Bool {
        if (this._roots.length > 0) {
            return true;
        } else {
            for (p in this._parents) {
                for (c in p.children()) {
                    this._roots.push(c);
                }
            }
            this._parents = [];
        }

        return (this._roots.length > 0);
    }

    public function next():Element {
        var rt:Element = this._roots.shift();
        this._parents.push(rt);
        return rt;
    }
}
