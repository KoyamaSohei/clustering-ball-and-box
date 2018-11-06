import { fromEvent , Subject, Observable, of, combineLatest} from 'rxjs';
import { map, switchMap} from 'rxjs/operators';

const init = new Subject();
const draw = new Subject();

draw.subscribe( ([color,url]: [string,string]) => {
  const img : HTMLImageElement = document.querySelector('img.' + color);
  img.src = url;
})

const onChange = (e: HTMLElement) : Observable<number> => {
  return (
    fromEvent(e,'change')
      .pipe(
        map((e: Event) => e.srcElement),
        map((e: HTMLInputElement) => Number(e.value)),
      )
  )
}

init.subscribe({
  complete: () => {
    of('h','s','v')
      .pipe( 
        map((c) => (Array.prototype.slice.call(document.querySelectorAll('input.' + c))).concat(c) )
      )
      .subscribe( ([min,max,c] : [HTMLElement,HTMLElement,string] ) => {
        combineLatest(onChange(min),onChange(max))
          .pipe(
            switchMap((val) => fetch(`/${c}/${val[0]}/${val[1]}`)),
            switchMap((res) => res.blob())
          )
          .subscribe( (v) => {
            const objurl = URL.createObjectURL(v);
            console.log(objurl);
            draw.next([c,objurl]);
          })
      })
  }
})


fromEvent(window,'load')
  .subscribe(() => init.complete())