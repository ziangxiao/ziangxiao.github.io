var test_file =
{"author" : "zxiao5", "date" : "2016", "size" : "18888", "files" : [{"name" : "test", "versions" : [{"number" : "1096", "author" : "zxiao5"}], "comments" : [{"content" : "finished", "author" : "zxiao5"}]}],};

//Project author tester
test( "test Project author ", function() {
  ok( test_file.author == "zxiao5", "Passed!" );
});

//File size tester
test( "test File size ", function() {
  ok( test_file.size == "18888", "Passed!" );
});

//Project date tester
test( "test Project date ", function() {
  ok( test_file.date == "2016", "Passed!" );
});


//Project files tester
test( "test Project files ", function() {
  ok( test_file.files.length == "1", "Passed!" );
});

//File name tester
test( "test Project files ", function() {
  ok( test_file.files[0].name == "test", "Passed!" );
});

//File author tester
test( "test File author ", function() {
  ok( test_file.files[0].comments[0].author == "zxiao5", "Passed!" );
});


//Project version tester
test( "test Project file version ", function() {
  ok( test_file.files[0].versions[0].number == "1096", "Passed!" );
});


//Comment content tester
test( "test File comment content ", function() {
  ok( test_file.files[0].comments[0].content == "finished", "Passed!" );
});


