const {test}=require('node:test');const assert=require('node:assert/strict');const M=require('../web/motion');
test('drag progress clamps at page boundaries',()=>{assert.equal(M.progress(100,500),.2);assert.equal(M.progress(-100,500),.2);assert.equal(M.progress(700,500),1);});
test('short slow drags return; deliberate distance and forward flicks commit',()=>{assert.equal(M.commit(18,400,2),false);assert.equal(M.commit(40,400,.1),false);assert.equal(M.commit(100,400,.1),true);assert.equal(M.commit(-40,400,-.8),true);assert.equal(M.commit(-40,400,.8),false);});
test('settle duration is bounded and matches remaining distance',()=>{assert.ok(M.duration(.9,true,0)<M.duration(.1,true,0));assert.ok(M.duration(.1,false,0)<M.duration(.9,false,0));});
test('turn endpoint reveals exact target page with no fade or rotation jump',()=>{for(const d of [-1,1]){const end=M.poses(1,d,400);assert.match(end.front,/rotateY\(0\.000deg\)/);assert.equal(end.back,'translate3d(0.00px,0,0)');}});
