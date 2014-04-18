from ..paper import Paper
from .. import repo
from ..configs import config
from ..uis import get_ui
from ..endecoder import EnDecoder


def parser(subparsers):
    parser = subparsers.add_parser('edit',
            help='open the paper bibliographic file in an editor')
    parser.add_argument('-m', '--meta', action='store_true', default=False,
            help='edit metadata')
    parser.add_argument('citekey',
            help='citekey of the paper')
    return parser


def command(args):

    ui = get_ui()
    meta = args.meta
    citekey = args.citekey

    rp = repo.Repository(config())
    try:
        paper = rp.pull_paper(citekey)
    except repo.InvalidReference as v:
        ui.error(v)
        ui.exit(1)

    coder = EnDecoder()
    if meta:
        encode = coder.encode_metadata
        decode = coder.decode_metadata
        suffix = '.yaml'
        raw_content = encode(paper.metadata)
    else:
        encode = coder.encode_bibdata
        decode = coder.decode_bibdata
        suffix = '.bib'
        raw_content = encode(paper.bibdata)

    while True:
        # Get new content from user
        raw_content = ui.editor_input(initial=raw_content, suffix=suffix)
        # Parse new content
        try:
            content = decode(raw_content)

            if meta:
                new_paper = Paper(paper.bibdata, citekey=paper.citekey,
                                  metadata=content)
            else:
                new_paper = Paper(content, metadata=paper.metadata)
                rp.rename_paper(new_paper, old_citekey=paper.citekey)
            break

        except repo.CiteKeyCollision:
            options = ['overwrite', 'edit again', 'abort']
            choice = options[ui.input_choice(
                options, ['o', 'e', 'a'],
                question='A paper already exists with this citekey.'
                )]

            if choice == 'abort':
                break
            elif choice == 'overwrite':
                paper = rp.push_paper(paper, overwrite=True)
                break
            # else edit again
        # Also handle malformed bibtex and metadata
