        // 画面リロード時にやること
        $(document).ready(function() {

            // 画面更新
            updateView();
            
            // 文字数取得する
            getFormLen('senderName');
            getFormLen('notifyTitle');
            getFormLen('notifyMessage');

            // カレンダーの値設定
            $('#reservedDate').datepicker({
                minDate: '+1d'
            });
        });
        

        /**
         * 送信日時のフォーマット設定
         */
        $(function() {
            // 外部ライブラリ使ってスラッシュを自動入力させる
            $('#reservedDate').formance('format_yyyy_mm_dd');

            // 時刻プルダウン
            $('#reservedTime').timepicker();
            $('#reservedTime').timepicker('option', 'step', '30');
            $('#reservedTime').timepicker('option', 'timeFormat', 'H:i');
        });


        /**
         * 一括選択
         */
        ///////////////////////////////////////////

        // チェックボックスがチェックされたら所属する都道府県を一括チェックする
        function checkedAll(areaName) {
            $('#'+areaName).on('click', function() {
                $('.'+areaName).prop('checked', this.checked);
            });
            $('.'+areaName).on('click', function() {
                var boxCnt     = $('.'+areaName).length;
                var checkedCnt = $('.'+areaName + ':checked').length;
                if (checkedCnt === boxCnt) {
                    $('#'+areaName).prop('checked', true);
                } else {
                    $('#'+areaName).prop('checked', false);
                }
            });
        }

        // 都道府県
        var areas = ['tohoku', 'kanto', 'chubu', 'kinki', 'shikoku', 'chugoku', 'kyushu'];
        for (var area in areas) {
            checkedAll(areas[area]);
        }

        // メディアランク
        checkedAll('allRank');

        ///////////////////////////////////////////


        // 各エリアのチェック数をカウントする関数
        function checkedCnt(areaName) {
            var areaCnt = $('#'+areaName+'s :checked').length;
            return areaCnt;
        }
        /**
        * 初期選択値の判定、設定する
         */
        ///////////////////////////////////////////
        
        // 都道府県
        function isNotSelectAny(currentVal) {
            return currentVal === 0;
        }

        // 各エリアのチェックされている都道府県の数を数える
        var areaCnt = [];
        for (var area in areas) {
            areaCnt.push(checkedCnt(areas[area]));
        }

        // 何も都道府県選択がない場合は、関東地方を初期値としてチェックする
        if (areaCnt.every(isNotSelectAny)) {
            $('#kanto').prop('checked', true);
            $('.kanto').prop('checked', true);
        }

        // メディアランク
        var rankCnt = checkedCnt('allRank');
        
        // メディアランクが何もチェックされていなければ初期値としてチャレンジをチェックする
        if (rankCnt === 0) {
            $('#チャレンジ').prop('checked', true);
        }

        // メディア入会期間
        var signUpCnt = checkedCnt('signUp');
        if (signUpCnt === 0) {
            $('#signUp7').prop('checked', true);
        }

        // ログイン期間
        var loginCnt = checkedCnt('login');
        if (loginCnt === 0) {
            $('#login7').prop('checked', true);
        }
        ///////////////////////////////////////////

        /**
         * 文字数入力制限
         */
        ///////////////////////////////////////////

        // 半角カナと全角を2byteその他半角文字を1byteで文字数カウントする関数
        function getLen(str) {
            var result = 0;
            for (var i=0; i<str.length; i++) {
                var chr = str.charCodeAt(i);
                if ((chr >= 0x00 && chr < 0x81) ||
                    (chr === 0xf8f0) ||
                    (chr >= 0xf8f1 && chr < 0xf8f4)) {
                    //半角文字の場合は1を加算
                    result += 1;
                } else {
                    //それ以外の文字の場合は2を加算
                    result += 2;
                }
            }
            //結果を返す
            return result;
        };

        // 文字数を表示する
        function getFormLen(elementName) {
            var inputData = $('#'+elementName).val();
            $('.'+elementName+'Counter').text(getLen(inputData));
        }

        // 各パラメータのbyte数を判定
        function checkLengthError(elementName, size) {
            $('#'+elementName).keyup(function() {
                var inputData = $(this).val();
                $('.'+elementName+'Counter').text(getLen(inputData));
                if (getLen(inputData) > size) {
                    buttonInActive('confirm');
                    return $('#'+elementName+'ErrorMsgId').text(size+'文字以内で入力してください');
                } else {
                    $('#'+elementName+'ErrorMsgId').text('');
                    return true;
                }
            });
        }

        ///////////////////////////////////////////

        /**
         * ボタン表示判定処理
         */
        ///////////////////////////////////////////
        // エラーメッセージとボタンの状態を更新する関数
        var updateView = function() {
            checkLengthError('senderName', 128);
            checkLengthError('notifyTitle', 256);
            checkLengthError('notifyMessage', 4000);
            isTimeTrue();
            if (($('#reservedDate').val()).trim() === "") {
                buttonInActive('confirm');
                return true;
            }
            if (($('#reservedTime').val()).trim() === "") {
                buttonInActive('confirm');
                return true;
            }
            if (($('#senderName').val()).trim() === "") {
                buttonInActive('confirm');
                return true;
            }
            if (($('#notifyTitle').val()).trim() === "") {
                buttonInActive('confirm');
                return true;
            }
            if (($('#notifyMessage').val()).trim() === "") {
                buttonInActive('confirm');
                return true;
            }
            buttonActive('confirm');
            return true;
        }

        // ボタンを非アクティブにする関数
        function buttonInActive(buttonName) {
            $('#'+buttonName).prop('disabled', true);
        }

        // ボタンをアクティブにする関数
        function buttonActive(buttonName) {
            $('#'+buttonName).prop('disabled', false);
        }

        // 各項目の空白チェック
        function isEmpty(elementName) {
            if (($('#'+elementName).val()).trim() === "") {
                buttonInActive('confirm');
                return true;
            }
        }

        // 各フォームがキーアップされた段階で評価
        function updateViewIfKeyup(elementName) {
            $('#'+elementName).keyup(function(e) {
                updateView();
            });
        }

        ///////////////////////////////////////////


        /**
         * 送信日時部分バリデーション
         */
        // 日付部分は半角数値とスラッシュ以外入力不可
        function setDateFormat(elementId) {
            var inputStr = elementId.value;
            while (inputStr.match(/[^\d\/]/)) {
                inputStr = inputStr.replace(/[^\d\/]/, "");
            }
            elementId.value = inputStr;
        }

        // 時刻部分は半角数値とコロン以外入力不可
        function setTimeFormat(elementId) {
            var inputStr = elementId.value;
            while (inputStr.match(/[^\d\:]/)) {
                inputStr = inputStr.replace(/[^\d\:]/, "");
            }
            elementId.value = inputStr;
        }

        // 時刻バリデーション
        function isTimeTrue() {
            $('#reservedTime').change(function() {
                var time = $('#reservedTime').val();
                if (!time.match(/^([01]?[0-9]|2[0-3]):([03]0)/)) {
                    buttonInActive('confirm');
                    return $('#reservedTimeErrorMsgId').text('正しい時刻を入力してください(時刻は30分刻みで入力できます)');
                } else {
                    $('#reservedTimeErrorMsgId').text('');
                    return true;
                }
            });
        }

        // 各項目の状態からビューの更新実施
        updateViewIfKeyup('reservedDate');
        updateViewIfKeyup('reservedTime');
        updateViewIfKeyup('senderName');
        updateViewIfKeyup('notifyTitle');
        updateViewIfKeyup('notifyMessage');


        /**
         * 以下、確認画面のjs
         */
        ///////////////////////////////////////////
        // ページ遷移したときのために$mediaDataではなく$_SESSIONを見るようにする
        var mediaCnt = <?= json_encode($_SESSION['data']['pagingCnt']); ?>;
        if (mediaCnt === 0) {
            buttonInActive('registration');
            $('#asmstIdErrorMsgId').text('該当するメディアはありません。抽出条件を変更してください');
        }

        // php側で進捗のたびにlogを上書きしている。それを一定時刻で読み込み表示する
            var Progress = (function() {
                function Progress(p) {
                    this.bar = document.querySelectorAll('#progressBar > .progressBarBody')[0];
                    this.p = p;
                    this.update();
                }
                Progress.prototype.update = function() {
                    this.bar.style.width = this.p + '%';
                }
                Progress.prototype.countup = function(data) {
                    if (this.p < 100) {
                        this.p = Number(data);
                    }
                    this.update();
                }
                return Progress;
            }());

            var updateProgress = function(progress) {
                $.ajax('./include/individualNotice/percent.log', {
                    dataType: 'text',
                    success: function(data) {
                        $('#progress').html('進捗状況: '+data+'%');
                        progress.countup(data);
                    }
                });
            }
            
            $('#set').on('click', function() {
                $('#progressArea').html('<div id="progressBar" class="progress"><div class="progressBarBody"></div></div>');
                var progress = new Progress(0);
                $('#progress').html('進捗状況: 0%');
                setInterval(function() {
                    updateProgress(progress);
                }, 1000);
            });
