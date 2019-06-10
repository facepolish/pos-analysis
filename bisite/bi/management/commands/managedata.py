from django.core.management.base import BaseCommand

from ...dashboard import KojitsuPos


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Fetch data from Oracle Server'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）
    def add_arguments(self, parser):
       parser.add_argument('all',  help = 'delete current data and overwrite with fatched data. It takes long time.')
#       parser.add_argument('-diff', help = 'Fetch latest data and append them on existing data')

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        if options['all']:
            KojitsuPos.refreshtables()
            self.stdout.write(self.style.SUCCESS('Successfully deleted old data and updated with latest POS data'))
        else:
            KojitsuPos.diffupdatetables()
            self.stdout.write(self.style.SUCCESS('Successfully appended POS data'))
            
