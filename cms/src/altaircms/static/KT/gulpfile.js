// -*- coding: utf-8 -*-
var fs = require('fs');
var gulp = require('gulp');
var child_process = require('child_process');

gulp.task('sync', function (){
    var s3_target = 's3://tstar/usersite/static/';
    var cur = fs.realpathSync('./');
    var organization_short_name = cur.split('/').pop();
    var s3_dst = s3_target + organization_short_name;
    var path = '*/**';
    gulp.watch(path, function (ev){
        var relpath = ev.path.replace(cur, '');
        var dst = s3_dst + relpath;
        console.log(dst);
        var cmd = 's3cmd put -P ' + ev.path + ' ' + dst;
        console.log(cmd);
        var child = child_process.exec(cmd, function (err, stdout, stderr){
            if (!err){
                console.log('stdout: ' + stdout);
                console.log('stderr: ' + stderr)
            } else {
                console.log(err);
                // err.code will be the exit code of the child process
                console.log(err.code);
                // err.signal will be set to the signal that terminated the process
                console.log(err.signal);
            }
        });
    });
});

gulp.task('default', function (){
    gulp.run('sync');
});
