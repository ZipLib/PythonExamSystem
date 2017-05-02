/**
* Created by Administrator on 2017-03-13.
*/

var timer;

questionNumber = function (i){
    document.write(i+1);
};



$(document).ready(function () {

//  点击改变选项颜色
    $("label").click(function(){
        $("label").removeClass("input_click");
        $(this).addClass("input_click");
    });
// ..
    function makeChoise(questionid){
        var data={"questionid": questionid}
        $.ajax({
             type: 'POST',
             url: "{{ url_for('main.delete_question') }}",
             data: data,
             dataType: 'json',
             success: function(data){
                 window.location.reload()
             },
             error: function(xhr, type){
                 alert('something wrong')
             },
        });
    }

// 获取选择的选项值 下1方调用
    getUserKey = function(n){
        var Check = "";
        // alert('checked check : '+$("[name='"+n+"']:checked").length);
        var checkedObj = $("[name='"+n+"']:checked");

        checkedObj.each(function(){
            var isCheck = this.value + "";
            Check += isCheck;
        });
        return Check;
    };

// 作答提交后的当前页响应    Test
    $("#submit2").click(function () {
        // clearTimeout(timer);
        // alert('submit2.')
        $(".qk").each(function(){
            //alert('each could be showed.');
            var td_key_id = $(this).attr("id");
            var question_id = td_key_id.substring(4,td_key_id.length);
            // alert(question_id+'----');

            var question_key = $("#s"+question_id+"ed").val();

            var user_key = getUserKey("question"+question_id);
            // alert(user_key);
            var html = "答案：" + question_key + "<br/>";
                html += "选择：" + user_key + "<br/>";
            var key_check = (user_key == question_key ? "true" : "err");
            html += "<img src=''  width='35' /><br/>";
            $("#show"+question_id).html(html);
            // var i = 0;
            // if(key_check){
            //     i++;
            // // }

        });
        // alert('...: '+$(".qk")[0].innerHTML)
    });

    //    DNF  集成后调用Ajax出错404
    function delete_question(question_id, question_type) {
        $.ajax({
            type: 'POST',
            url: "{{ url_for('main.delete_question') }}",
            data: {
                question_id: question_id,
                question_type: question_type
            },
            dataType: 'json',
            success: function (data) {
                window.location.reload()
            },
            error: function (xhr, type) {
                alert('delete question error type: '
                    +type+'---- status:'+xhr.status+'---- readyState:'+xhr.readyState
                    +'---- responseText: '+xhr.responseText)
            }
        })
    }

    //  删除题目    DNF  在js包调用Ajax 404
    $("#delete_question").click(function () {
        alert('delete work.');
        var question_id = $("#hide_id").html();
        var question_type = $("#hide_type").text();
        delete_question(question_id, question_type);
    });

    //
    function delete_exam(exam_id, exam_choice) {
        $.ajax({
            type: 'POST',
            url: "{{ url_for('main.delete_exam') }}",
            data: {
                exam_id: exam_id,
                exam_choice:exam_choice
            },
            dataType: 'json',
            success: function (data) {
                window.location.reload()
            },
            error: function (xhr, type) {
                alert('delete exam error type: '
                    +type+'---- status:'+xhr.status+'---- readyState:'+xhr.readyState
                    +'---- responseText: '+xhr.responseText)
            }
        })
    };

})

// 全屏
function full_screen() {
    var docElm = document.documentElement;
    //W3C
    if (docElm.requestFullscreen) {
        docElm.requestFullscreen();
    }
    //FireFox
    else if (docElm.mozRequestFullScreen) {
        docElm.mozRequestFullScreen();
    }
    //Chrome等
    else if (docElm.webkitRequestFullScreen) {
        docElm.webkitRequestFullScreen();
    }
    //IE11
    else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen();
    }
}
// 退出全屏
function exit_full_screen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    }
    else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    }
    else if (document.webkitCancelFullScreen) {
        document.webkitCancelFullScreen();
    }
    else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
}
// 禁止复制
    document.oncopy=function(e){
    return false;
    };
//禁止右键  （考试主页面）
    document.oncontextmenu=function(e){
        return false;
    };

//禁止刷新  （考试主页面）
    document.onkeydown = function(e){
        e = window.event || e;
        var keycode = e.keyCode || e.which;
        if( keycode = 116){
            if(window.event){// ie
                try{e.keyCode = 0;}catch(e){}
                e.returnValue = false;
            }else{// ff
                e.preventDefault();
            }
        }
    };

// 禁止esc键盘    DNF    not work
    function killEsc(){
        if(window.event.keyCode==27){
            window.event.keyCode=0;
            window.event.returnValue=false;
        }
    }
    document.onload = killEsc;
    document.onkeydown = killEsc;
    function keydown(e){
        if(e==null)
            e = window.event;
        if(e.keyCode==27|| e.keyCode==8){
            e.keyCode=0;
            e.cancelBubble=true;
            e.returnValue=false;
            return false;
        }
    }
    document.onkeypress = keydown;
    document.onkeydown = keydown;

// 禁止截屏，通过清除剪切板实现
    function clearShearPlate() {
        try {
            if (clipboardData.getData("Text") || clipboardData.getData("HTML") || clipboardData.getData("URL")) {
                null;
            clipboardData.setData("Text", "");
            }
        }
        catch (e) {
            clipboardData.setData("Text", "")
        }
        setTimeout("clearShearPlate()", 500)
    }

// 验证自定考试页表单不为空    DNF
    var MyValidator = function() {
        var handleSubmit = function() {
            $('.form-horizontal').validate({
                errorElement : 'span',
                errorClass : 'help-block',
                focusInvalid : false,
                rules : {
                    name : {
                        required : true
                    },
                    password : {
                        required : true
                    },
                    intro : {
                        required : true
                    }
                },
                messages : {
                    name : {
                        required : "Username is required."
                    },
                    password : {
                        required : "Password is required."
                    },
                    intro : {
                        required : "Intro is required."
                    }
                },
                highlight : function(element) {
                    $(element).closest('.form-group').addClass('has-error');
                },
                success : function(label) {
                    label.closest('.form-group').removeClass('has-error');
                    label.remove();
                },
                errorPlacement : function(error, element) {
                    element.parent('div').append(error);
                },
                submitHandler : function(form) {
                    form.submit();
                }
            });
            $('.form-horizontal input').keypress(function(e) {
                if (e.which == 13) {
                    if ($('.form-horizontal').validate().form()) {
                        $('.form-horizontal').submit();
                    }
                    return false;
                }
            });
        };
        return {
            init : function() {
                handleSubmit();
            }
        };
    }();

// 倒计时    DN U
    function countdown ()
    {
        var end = new Date (2017, 4, 1, 3);
        var now = new Date ();

        var m = Math.round ((end - now) / 1000);
        var day = parseInt (m / 24 / 3600);
        var hours = parseInt ((m % (3600 * 24)) / 3600);
        var minutes = parseInt ((m % 3600) / 60);
        var seconds = m % 60;

        if (m < 0)
        {
            document.getElementById ("clock").innerHTML = '0';
            return;
        }
        document.getElementById ("clock").innerHTML = "离开始还剩" + day + "天" + hours + "小时" + minutes + "分钟" + seconds
                + "秒";
        setTimeout ('countdown()', 1000);
    }
    window.onload = function ()
    {
        countdown ();
    }
// $(document).ready(function () {
//     $('button#qt').click(function () {
//         alert('button #qt is : ' + $(this).attr("onclick"));
//     });
// })

// function button_click(obj){
//     $.each($('button'),function(){
//         $(this).removeClass("my-buttons")});
//     $(obj).addClass("my-buttons");
// }

// {#        function choose_question(question_type) {#}
// {##}
// {#            $.ajax({#}
// {#                type: 'POST',#}
// {#                url: "{{ url_for('main.question_list')}}",#}
// {#                data: JSON.stringify({"question_type": question_type}),#}
// {#                dataType: 'json',    #}
// {#                async:false,#}
// {#                success: function(data) {#}
// {#                    window.location.reload()#}
// {#                },#}
// {#                error: function(xhr, type) {#}
// {#                    alert('choose question error type: '#}
// {#                        +type+'status:'+xhr.status+'readystate'+xhr.readyState#}
// {#                        +'responseText: '+xhr.responseText)#}
// {#                }#}
// {#            });#}
// {#        }#}
