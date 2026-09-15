// Do not erode/dilate a finely sampled smooth curve once per vertex.
const a3OldGarment=garment,a3OldInk=inkPath;
garment=function(loop,gap,radius){
 const p=insetClean(loop,gap);
 if(!p||p.length<3)return a3OldGarment(loop,gap,radius);
 return {inset:gap,radius,cores:[p]};
};
inkPath=function(ctx,pts,r,cont){roundedPath(ctx,pts,r,cont);return pts;};
