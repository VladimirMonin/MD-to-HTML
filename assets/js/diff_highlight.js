document.addEventListener('DOMContentLoaded', () => {
    // Убедимся, что diff_match_patch загружен
    if (typeof diff_match_patch === 'undefined') {
        console.error('diff_match_patch not loaded.');
        return;
    }

    window.applyDiffHighlight = () => {
        const dmp = new diff_match_patch();

        document.querySelectorAll('.diff-wrapper').forEach(wrapper => {
            const beforeCode = wrapper.querySelector('.diff-container:nth-child(1) code');
            const afterCode = wrapper.querySelector('.diff-container:nth-child(2) code');

            if (!beforeCode || !afterCode) return;

            const text1 = beforeCode.textContent;
            const text2 = afterCode.textContent;

            const diffs = dmp.diff_main(text1, text2);
            dmp.diff_cleanupSemantic(diffs);

            beforeCode.innerHTML = createHtml(diffs, -1);
            afterCode.innerHTML = createHtml(diffs, 1);
        });
    };

    function createHtml(diffs, type) {
        let html = '';
        for (const [op, data] of diffs) {
            const text = data.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
            if (op === 0) { // common
                html += text;
            } else if (op === type) { // insert or delete
                const className = type === 1 ? 'diff-add' : 'diff-sub';
                html += `<span class="${className}">${text}</span>`;
            }
        }
        return html;
    }
    
    // Вызываем после небольшой задержки, чтобы highlight.js успел отработать
    setTimeout(() => {
        // Сначала подсветка синтаксиса
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        // Затем наша подсветка diff
        window.applyDiffHighlight();
        // И наконец, синхронизация высоты
        window.syncDiffBlockHeights();
    }, 100);
});

window.syncDiffBlockHeights = () => {
    const diffWrappers = document.querySelectorAll('.diff-wrapper');

    diffWrappers.forEach(wrapper => {
        const beforeContainer = wrapper.querySelector('.diff-container:nth-child(1) pre');
        const afterContainer = wrapper.querySelector('.diff-container:nth-child(2) pre');

        if (!beforeContainer || !afterContainer) {
            return;
        }

        beforeContainer.style.height = 'auto';
        afterContainer.style.height = 'auto';

        const beforeHeight = beforeContainer.scrollHeight;
        const afterHeight = afterContainer.scrollHeight;

        const maxHeight = Math.max(beforeHeight, afterHeight);

        beforeContainer.style.height = `${maxHeight}px`;
        afterContainer.style.height = `${maxHeight}px`;
    });
};

window.addEventListener('resize', window.syncDiffBlockHeights);
