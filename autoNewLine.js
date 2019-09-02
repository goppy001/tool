/* テキストエリアで入力文字を一定文字数で自動改行する関数
主にテキストエリアに入れた文字をsqlのin()句で投げる場合などで使用
*/

function autoDoNewLine(elementId) {
    var limitCount   = 15; // example.
    var inputData    = $(elementId).val();
    var inputDataArr = inputData.split(/[\r\n|\n|\r]/);
    var resultArr    = [];
    inputDataArr.forEach( function(idData) {
        var idValCount = idData.length;
        if (!idData || !idValCount) {
            return false;
        }
        if (idValCount <= limitCount) {
            resultArr.push(idData);
        } else {
            var index = 0;
            var start = index;
            var end   = start + limitCount;
            while (start < idValCount) {
                resultArr.push(idData.substring(start, end));
                index++;
                start = end;
                end   = start + limitCount;
            }
            $(elementId).val(resultArr.join('\n'));
        }
    });
}
