var entries = null;

function render_entry(entry){
  var html = '<div>';
  // header
  html += '<div>';
  html += '<dl class="dl-horizontal">';
  html += '<dt> date </dt> <dd>' + entry.header.date + '</dd>';
  html += '<dt> tag </dt> <dd>' + entry.header.tags + '</dd>';
  html += '</dl>';
  html += '</div>';  //end of header
  // body
  html += '<div>';
  html += entry.body;
  html += '</div>';  //end of body

  html += '</div>';  //end of entry

  return html;
}


function save(){
  console.log('save');
  var entry_txt = $('#editor').val();
  console.log(entry_txt);
  var payload = { body: entry_txt };
  console.log(JSON.stringify(payload));

  // couldn't get JSON POST to work, sending text instead
  // $.post( "entry", entry_txt, null, 'json');
  // $.post( "entry", entry_txt);
  $.ajax({
    url:"entry",
    type:"POST",
    data:JSON.stringify(payload),
    contentType:"application/json; charset=utf-8",
    dataType:"json",
    success: null
  })
}


// function clear(){
//   console.log('clear');
//   //$('#editor').text('---\n---');
// }

function get_date(){
  var now = new Date();
  var date_str = '';
  if (now.getDate() < 10) date_str += '0';
  date_str += now.getDate();
  date_str += '-';

  if (now.getMonth() + 1 < 10) date_str += '0';
  date_str += now.getMonth() + 1;
  date_str += '-';

  date_str += now.getFullYear();
  date_str += ' ';

  if (now.getHours() < 10) date_str += '0';
  date_str += now.getHours();
  date_str += ':';

  if (now.getMinutes() < 10) date_str += '0';
  date_str += now.getMinutes();

  return date_str;
}

$( document ).ready(function(){

  var start_txt = '---\n';
  start_txt += 'date: ' + get_date() + '\n';
  start_txt += 'tag: \n';
  start_txt += '---\n\n';

  $('#editor').val(start_txt);



  // requesting entries from backend
  $.get("entry", function( data ) {
    entries = data;
    //alert( "Got entries." );
    console.log(data);

    console.log('looping entries');
    for(var i=0; i < entries.length; i++){
        html = render_entry(entries[i]);
        $('#entry_list').append(html);
    }
  });



  $('#btnSave').click(function(){
    save();
  });

});
