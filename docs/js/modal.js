document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems, '');
  });

  // Or with jQuery

  $(document).ready(function(){
    $('.modal').modal();
  });
