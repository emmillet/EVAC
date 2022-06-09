function cal_creator(events){
  var ev = [];
  // document.write(events[0]);
  // document.write(events[0][0]);
  var un_matched = Boolean(true);
  for (var event of events){
    un_matched = true;
    date = new Date(event[0][0], event[0][1], event[0][2])
    for (var i = 0; i < ev.length; i++){
      if(ev[i].Date.getTime() === date.getTime()){
        var title = ev[i].Title + ' and ' + new String(event[1]) + ": " + new String(event[2]);
        ev.splice(i,1);
        ev.push({'Date': date, 'Title': title});
        un_matched = false;
        break;
      }
    }
    if(un_matched){
      ev.push({'Date': date, 'Title': new String(event[1]) + ": " + new String(event[2])});
    }
  }
  // document.write(ev);
  var settings = {};
  var element = document.getElementById('caleandar');
  caleandar(element, ev, settings);
}